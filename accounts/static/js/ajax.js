function ajax_like_func(url){
    $.ajax({
        url: url,
        type: 'get',
        success: function (data){
            div = document.getElementById('id_ajax_like')
            span = document.getElementById('id-ajax-favorite-number')
            if (data['is_liked']){
                div.children[0].style.display=''
                div.children[1].style.display='none'
                span.innerText=data['favorite_number']
            }else {
                div.children[0].style.display='none'
                div.children[1].style.display=''
                span.innerText=data['favorite_number']
            }
        }
        })
}
function ajax_bookmark_func(url){
    $.ajax({
        url: url,
        type: 'get',
        success: function (data){
            div = document.getElementById('id-ajax-bookmark-div')
            span = document.getElementById('id-ajax-bookmark-p')
            if (data['is_bookmarked']){
                div.children[0].style.display=''
                div.children[1].style.display='none'
                span.innerText='bookmarked'
            }else{
                div.children[0].style.display='none'
                div.children[1].style.display=''
                span.innerText='add to bookmark'
            }
        }
    })
}
function ajax_add_one_func(url){
    $.ajax({
        url: url,
        type: 'get',
        success: function (data){
            if (data['should_hide']){
                div = document.getElementById('id-ajax-add-one-'+data['variant_id'])
                div.style.visibility = 'hidden'
                span = document.getElementById('id-ajax-quantity-'+data['variant_id'])
                span.innerText = data['quantity']
                price = document.getElementById('id-ajax-price-'+data['variant_id'])
                price.innerText = data['price'][data['variant_id']]
                total_price = document.getElementById('id-ajax-total-price')
                total_price.innerText = data['total_price']
                navbar_cart = document.getElementsByClassName('class-ajax-navbar-cart')[0]
                navbar_cart.innerText = data['cart_len']
            }else {
                span = document.getElementById('id-ajax-quantity-'+data['variant_id'])
                span.innerText = data['quantity']
                price = document.getElementById('id-ajax-price-'+data['variant_id'])
                price.innerText = data['price'][data['variant_id']]
                total_price = document.getElementById('id-ajax-total-price')
                total_price.innerText = data['total_price']
                navbar_cart = document.getElementsByClassName('class-ajax-navbar-cart')[0]
                navbar_cart.innerText = data['cart_len']
            }
        }
    })
}
function ajax_remove_one_func(url){
    $.ajax({
        url: url,
        type: 'get',
        success: function (data){
            if (data['should_hide']){
                div = document.getElementById('id-ajax-remove-one-'+data['variant_id'])
                div.style.visibility = 'hidden'
                span = document.getElementById('id-ajax-quantity-'+data['variant_id'])
                span.innerText = data['quantity']
                tr = document.getElementById('id-ajax-delete-variant-'+data['variant_id'])
                tr.style.display = 'none'
                tr = document.getElementById('id-ajax-cart-img-delete-'+data['variant_id'])
                tr.style.display = 'none'
                total_price = document.getElementById('id-ajax-total-price')
                total_price.innerText = data['total_price']
                price = document.getElementById('id-ajax-price-'+data['variant_id'])
                price.innerText = data['price'][data['variant_id']]
                navbar_cart = document.getElementsByClassName('class-ajax-navbar-cart')[0]
                navbar_cart.innerText = data['cart_len']
                if (data['total_price'] === 0){
                    price = document.getElementById('id-ajax-delete-all')
                    price.remove()
                    price = document.getElementById('id-ajax-buy-button')
                    price.remove()
                    navbar_cart.remove()
                }
            }else {
                div = document.getElementById('id-ajax-add-one-'+data['variant_id'])
                div.style.visibility = ''
                span = document.getElementById('id-ajax-quantity-'+data['variant_id'])
                span.innerText = data['quantity']
                total_price = document.getElementById('id-ajax-total-price')
                total_price.innerText = data['total_price']
                price = document.getElementById('id-ajax-price-'+data['variant_id'])
                price.innerText = data['price'][data['variant_id']]
                navbar_cart = document.getElementsByClassName('class-ajax-navbar-cart')[0]
                navbar_cart.innerText = data['cart_len']
            }
        }
    })
}
function ajax_remove_func(url){
    $.ajax({
        url: url,
        type: 'get',
        success: function (data){
            tr = document.getElementById('id-ajax-delete-variant-'+data['variant_id'])
            tr.style.display = 'none'
            tr = document.getElementById('id-ajax-cart-img-delete-'+data['variant_id'])
            tr.style.display = 'none'
            total_price = document.getElementById('id-ajax-total-price')
            total_price.innerText = data['total_price']
            navbar_cart = document.getElementsByClassName('class-ajax-navbar-cart')[0]
            navbar_cart.innerText = data['cart_len']
            if (data['total_price'] === 0){
                price = document.getElementById('id-ajax-delete-all')
                price.remove()
                price = document.getElementById('id-ajax-buy-button')
                price.remove()
                navbar_cart.remove()
            }
        }
    })
}
function ajax_remove_bookmark(url){
    $.ajax({
        url: url,
        type: 'get',
        success: function (data){
            console.log('henlo fren')
            bookmark = document.getElementById('id-ajax-remove-bookmark-'+data['watch_id'])
            bookmark.remove()
        }
    })
}