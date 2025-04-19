import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images, safe_json_post
from .models import Chat
from .forms  import ChatForm
from user.models import Profile

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page=1):
    logger.debug('start Chat list_view')

    PAGE_SIZE = 40 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    object_list = Chat.objects.select_related('profile').order_by('-order_by_at')  # order_by_at の降順で取得
    
    if object_list.exists():
        logger.debug('object_list exists')
        paginator = Paginator(object_list, PAGE_SIZE)
        try:
            display_object_list = paginator.page(page)
        except Exception as e:
            logger.warning(f'couldnt catch the display_object_list page={page}, error={e}')
            display_object_list = paginator.page(1)        
        link_object_list = display_object_list.paginator.get_elided_page_range(
            page, on_each_side=PAGINATION_ON_EACH_SIDE, on_ends=PAGINATION_ON_ENDS
        )
    else:
        logger.debug('object_list not exists')
        display_object_list = []
        link_object_list = []

    context = {'display_object_list': display_object_list, 'link_object_list': link_object_list}

    logger.info('return render chat/list.html')
    return render(request, 'chat/list.html', context)


def detail_view(request, pk):
    logger.info('start Chat detail_view')

    logger.debug('get Chat object(pk)')
    chat = get_object_or_404(Chat, pk=pk)

    context = {'object': chat}

    logger.debug('return render chat/detail.html')
    return render(request, 'chat/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Chat create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = ChatForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Chat form.is_valid')
            title_data = form.cleaned_data['title']
            context_data = form.cleaned_data['context']
            images_data = form.cleaned_data.get('images')
            author_data = form.cleaned_data['author']
            profile_data = None # initial setting
            pic_data = request.user.profile
            
            # "None"と入力されていたら入力者がAuthor(=Profile)で"author"項目はNone設定
            if author_data != "None":
                pass
            else:
                # 存在しない場合に例外を発生させる
                profile_data = get_object_or_404(Profile, user1=request.user)

            try:
                chat = Chat.objects.create(
                    title = title_data,
                    context = context_data,
                    images = None, # 画像はまだ保存しない
                    author = author_data,
                    profile = profile_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Chat object: {e}')
                logger.info('return render chat/create.html')
                return render(request, 'chat/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                chat.images = create_images(chat, images_data)

                try:
                    logger.debug('save new images_data')
                    chat.save()
                except Exception as e:
                    logger.error(f'couldnt save the images_data in Chat object: {e}')

            logger.info('return redirect chat:list')
            return redirect('chat:list')
        else:
            logger.error('form is invalid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = ChatForm()
        context = {'form': form}
    
    logger.info('return render chat/create.html')
    return render(request, 'chat/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Chat update_view')

    logger.debug('get Chat object(pk)')
    chat = get_object_or_404(Chat, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = ChatForm(request.POST, request.FILES)
        context = {'object': chat, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            chat.title = form.cleaned_data['title']
            chat.context = form.cleaned_data['context']
            chat.author = form.cleaned_data['author']
            chat.updated_pic = request.user.profile

            images_data = form.cleaned_data.get('images')
            delete_images_flg = form.cleaned_data.get('delete_images_flg')

            if images_data: # File Selected
                logger.debug('images_data exists')
                chat.images = update_images(chat, images_data)
            elif delete_images_flg and chat.images:
                logger.debug('delete_images exists')
                delete_images(chat)
                chat.images = None
                
            try:
                logger.debug('save updated Chat object')
                chat.save()
            except Exception as e:
                logger.error(f'couldnt save the Chat object: {e}')

            logger.info('return redirect chat:list')
            return redirect('chat:list')
        else:
            logger.error('form not is_valid.')
            logger.error(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = ChatForm(instance=chat) # putback the form
        context = {'object': chat, 'form': form}
    
    logger.info('return render chat/update.html')
    return render(request, 'chat/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Chat delete_view')

    logger.debug('get Chat object(pk)')
    chat = get_object_or_404(Chat, pk=pk)
    context = {'object': chat}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if chat.images:
            delete_images(chat)
        
        try:
            logger.debug('delete old Chat object')
            chat.delete()
        except Exception as e:
            logger.error(f'couldnt delete Chat object: {e}')

        logger.info('return redirect chat:list')
        return redirect('chat:list')
    else:
        logger.info('GET method')
    
    logger.info('return render chat/delete.html')
    return render(request, 'chat/delete.html', context)

@login_required
def push_likes(request, pk):
    logger.info('start Chat push_likes')
    return safe_json_post(request, lambda: _push_likes_logic(request, pk))

def _push_likes_logic(request, pk):
    chat = get_object_or_404(Chat, id=pk)
    logger.debug(f'get Chat object(pk)={chat}')

    chat.push_likes(request)

    logger.info(f'return likes:{chat.likes}')
    return JsonResponse({'likes': f'({chat.likes})'})

@login_required
def age_order_by_at(request, pk):
    logger.info('start Chat age_order_by_at')
    return safe_json_post(request, lambda: _age_order_by_at_logic(request, pk))

def _age_order_by_at_logic(request, pk):
    chat = get_object_or_404(Chat, id=pk)
    logger.debug(f'get Chat object(pk)={chat}')

    chat.age_order_by_at(request)

    logger.info('return True')
    return JsonResponse({'status': 'success'})
