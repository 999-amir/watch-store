from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views import View
from .models import CarouselModel, WatchModel, WatchBrandModel, WatchColorModel, WatchBandLockModel, WatchSystemModel, \
    WatchFaceShapeModel, WatchFaceMaterialModel, WatchBandMaterialModel, WatchVariantModel, WatchSeenModel, CommentModel
from django.db.models import Q, Min, Max
from .filters import WatchFilterRequired, WatchFilterUnrequired
from .forms import CommentForm, CommentReplyForm
from django.contrib import messages
from django.core.paginator import Paginator
from urllib.parse import urlencode
from django.http import JsonResponse


class ProductsView(View):
    def get(self, request):  # category pk and slug used for brand category
        watches_required = WatchModel.objects.filter(is_required=True).order_by('-updated')
        watches_unrequired = WatchModel.objects.filter(is_required=False).order_by('-updated')
        carousels = CarouselModel.objects.all().order_by('-updated')
        search = request.GET.get('search')
        if search is not None:
            watches_required = watches_required.filter(Q(brand__Brand__icontains=search) | Q(name__icontains=search))
            watches_unrequired = watches_unrequired.filter(
                Q(brand__Brand__icontains=search) | Q(name__icontains=search))

        # category for filter
        brands = WatchBrandModel.objects.all()
        colors = WatchColorModel.objects.all()
        band_locks = WatchBandLockModel.objects.all()
        systems = WatchSystemModel.objects.all()
        face_shapes = WatchFaceShapeModel.objects.all()
        face_materials = WatchFaceMaterialModel.objects.all()
        band_materials = WatchBandMaterialModel.objects.all()

        # filter
        filters_required = WatchFilterRequired(request.GET, queryset=watches_required)
        watches_required = filters_required.qs
        min_price_f = WatchModel.objects.aggregate(min_p=Min('min_price'))  # minimum price filter
        min_price_f = int(min_price_f['min_p'])
        max_price_f = WatchModel.objects.aggregate(max_p=Max('min_price'))  # maximum price filter
        max_price_f = int(max_price_f['max_p'])

        filter_unrequired = WatchFilterUnrequired(request.GET, queryset=watches_unrequired)
        watches_unrequired = filter_unrequired.qs
        color_ids = [int(i) for i in request.GET.getlist('color')]
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if color_ids:
            watches_required = watches_required.filter(rel_watch_variants__face_color_id__in=color_ids)
            watches_unrequired = []
        if min_price or max_price:
            watches_unrequired = []

        paginator = Paginator(watches_required, 30)  # change it later
        page_url_data = request.GET.copy()
        if 'page' in page_url_data:
            del page_url_data['page']
        page_num = request.GET.get('page')
        watches_required = paginator.get_page(page_num)

        context = {
            'watches_required': watches_required,
            'watches_unrequired': watches_unrequired[:10],
            'carousels': carousels,
            'last_search': search,
            # for filter
            'brands': brands,
            'colors': colors,
            'band_locks': band_locks,
            'systems': systems,
            'face_shapes': face_shapes,
            'face_materials': face_materials,
            'band_materials': band_materials,
            'filters': filters_required,
            'min_price_f': min_price_f,
            'max_price_f': max_price_f,
            # pagination
            'page_url_data': urlencode(page_url_data)
        }
        return render(request, 'product/products.html', context)


class DetailView(View):
    form_class = CommentForm
    form_reply_class = CommentReplyForm

    def get(self, request, watch_pk, slug):
        watch = get_object_or_404(WatchModel, pk=watch_pk)
        selected_watch = WatchVariantModel.objects.filter(id=watch.variant_id_min_price).first()  # it should be changed
        same_brand_watches = watch.brand.rel_watch_brands.all()[:5]
        # comments
        comments = CommentModel.objects.filter(product=watch, is_reply=False, can_show=True)
        reply_comments = CommentModel.objects.filter(product=watch, is_reply=True)

        color_id = request.GET.get('color_id')
        if color_id:
            selected_watch = watch.rel_watch_variants.get(face_color_id=color_id)

        # check user seen with ip
        ip = request.META.get('REMOTE_ADDR')
        if request.user.is_authenticated:
            if not WatchSeenModel.objects.filter(watch=watch, ip=ip, user=request.user).exists():
                WatchSeenModel.objects.create(watch=watch, ip=ip, user=request.user)
                watch.total_seen += 1
                watch.save()
        else:
            if not WatchSeenModel.objects.filter(watch=watch, ip=ip, user=None).exists():
                WatchSeenModel.objects.create(watch=watch, ip=ip)
                watch.total_seen += 1
                watch.save()

        # end check user seen with ip
        # like checker
        is_user_liked = watch.like_checker(request.user)
        is_user_bookmarked = watch.bookmark_checker(request.user)

        context = {
            'watch': watch,
            'selected_watch': selected_watch,
            'same_brand_watches': same_brand_watches,
            'is_user_liked': is_user_liked,
            'is_user_bookmarked': is_user_bookmarked,
            # comments
            'comments': comments,
            'reply_comments': reply_comments,
            'comment_form': self.form_class(),
            'reply_comment_form': self.form_reply_class()
        }

        return render(request, 'product/details.html', context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cm = form.save(commit=False)
            cm.user = request.user
            cm.product = get_object_or_404(WatchModel, pk=kwargs['watch_pk'])
            cm.save()
            messages.success(request, 'پیام شا با موفقیت ثبت شد و بعد از بررسی در سایت قرار خواهد گرفت', 'msg-bg-success')
            return redirect('product:details', kwargs['watch_pk'], kwargs['slug'])
        context = {
            'comment_form': form,
        }
        return render(request, 'product/details.html', context)


class CommentReplyView(View):
    form_class = CommentReplyForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, watch_pk, comment_id):
        watch = get_object_or_404(WatchModel, id=watch_pk)
        comment = get_object_or_404(CommentModel, id=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            cm = form.save(commit=False)
            cm.user = request.user
            cm.product = watch
            cm.reply = comment
            cm.is_reply = True
            cm.save()
            messages.success(request, 'پیام شما با موفقیت ثبت شد و بعد از بررسی در سایت قرار خواهد گرفت', 'msg-bg-success')
        context = {
            'comment_reply_form': form,
        }
        return redirect('product:details', watch.pk, watch.slug)


class LikeWatchView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, watch_pk, slug):
        watch = get_object_or_404(WatchModel, pk=watch_pk)
        if watch.likes.filter(id=request.user.id).exists():
            watch.likes.remove(request.user)
            watch.total_favorite -= 1
        else:
            watch.likes.add(request.user)
            watch.total_favorite += 1
        watch.save()
        data = {
            'is_liked': watch.like_checker(request.user),
            'favorite_number': watch.total_favorite
        }
        return JsonResponse(data)


class BookmarkClickView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ذخیره در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, watch_pk):
        watch = get_object_or_404(WatchModel, pk=watch_pk)
        if watch.bookmark.filter(id=request.user.id).exists():
            watch.bookmark.remove(request.user)
        else:
            watch.bookmark.add(request.user)
        data = {
            'is_bookmarked': watch.bookmark_checker(request.user)
        }
        return JsonResponse(data)


class DeleteBookmarkedView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از حذف ذخیره در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, watch_pk):
        watch = get_object_or_404(WatchModel, pk=watch_pk)
        watch.bookmark.remove(request.user)
        data = {
            'watch_id': watch.id
        }
        return JsonResponse(data)
