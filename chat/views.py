import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images
from .models import Chat
from .forms  import ChatForm
from user.models import Profile

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page_cnt=1):
    logger.debug('start Chat list_view')

    page_size = 40 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    object_list = Chat.objects.order_by('-order_by_at').all()  # order_by_at の降順で取得
    
    if object_list.exists():
        logger.debug('object_list exists')
        paginator = Paginator(object_list, page_size)
        try:
            display_object_list = paginator.page(page_cnt)
        except:
            logger.warning('couldnt catch the display_object_list page_cnt=', page_cnt)
            display_object_list = paginator.page(1)        
        link_object_list = display_object_list.paginator.get_elided_page_range(
            page_cnt, on_each_side=onEachSide, on_ends=onEnds
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
    object = get_object_or_404(Chat, pk=pk)

    context = {'object': object}

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
            
            if author_data != "None":
                pass
            else:
                # 存在しない場合に例外を発生させる
                profile_data = get_object_or_404(Profile, user1=request.user)

            try:
                object = Chat.objects.create(
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
                object.images = create_images(object, images_data)

                try:
                    logger.debug('save new images_data')
                    object.save()
                except:
                    logger.error(f'couldnt save the images_data in Chat object: {e}')

            logger.info('return redirect chat:list')
            return redirect('chat:list')
        else:
            logger.error('form is invalid.')
            print(form.errors)  # エラー内容をログに出力
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
    object = get_object_or_404(Chat, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = ChatForm(request.POST, request.FILES)
        context = {'object': object, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            object.title = form.cleaned_data['title']
            object.context = form.cleaned_data['context']
            object.author = form.cleaned_data['author']
            object.author = form.cleaned_data['author']
            object.updated_pic = request.user.profile

            images_data = form.cleaned_data.get('images')

            if images_data: # File Selected
                logger.debug('images_data exists')
                object.images = update_images(object, images_data)

            try:
                logger.debug('save updated Chat object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the Chat object: {e}')

            logger.info('return redirect chat:list')
            return redirect('chat:list')
        else:
            logger.error('form not is_valid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = ChatForm(instance=object) # putback the form
        context = {'object': object, 'form': form}
    
    logger.info('return render chat/update.html')
    return render(request, 'chat/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Chat delete_view')

    logger.debug('get Chat object(pk)')
    object = get_object_or_404(Chat, pk=pk)
    context = {'object': object}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if object.images:
            delete_images(object)
        
        try:
            logger.debug('delete old Chat object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete Chat object: {e}')

        logger.info('return redirect chat:list')
        return redirect('chat:list')
    else:
        logger.info('GET method')
    
    logger.info('return render chat/delete.html')
    return render(request, 'chat/delete.html', context)

@csrf_exempt  # 関数デコレータに変更
@login_required
def push_likes(request, pk):
    logger.info('start Chat push_likes')

    if request.method == 'POST':
        logger.info('POST method')

        chat = get_object_or_404(Chat, id=pk)
        logger.debug(f'get Chat object(pk)={chat}')

        # いいね処理を実行
        chat.push_likes(request)

        # Ajaxにいいね数を返す
        logger.info(f'return likes:({chat.likes})')
        return JsonResponse({'likes': f'({chat.likes})'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt  # 関数デコレータに変更
@login_required
def age_order_by_at(request, pk):
    logger.info('start Chat age_order_by_at')

    if request.method == 'POST':
        logger.info('POST method')

        chat = get_object_or_404(Chat, id=pk)
        logger.debug(f'get Chat object(pk)={chat}')

        # アゲ処理を実行
        chat.age_order_by_at(request)

        # Ajaxにいいね数を返す
        logger.info('return True')
        return JsonResponse({'status': 'True'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)