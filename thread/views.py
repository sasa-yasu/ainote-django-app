from django.conf import settings
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import disp_qr_code
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes
from .models import Thread, ThreadChat
from .forms  import ThreadForm, ThreadChatForm
from user.models import Profile

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page_cnt=1):
    logger.debug('start Thread list_view')

    page_size = 12 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    # カテゴリ検索
    search_category_choice = request.GET.getlist('search_category_choice')
    logger.debug(f'search_category_choice: {search_category_choice}')
    # 選択肢のバリデーション
    valid_choices = [choice[0] for choice in Thread.CATEGORY_CHOICES]
    logger.debug(f'valid_choices: {valid_choices}')
    category_choice = [choice for choice in search_category_choice if choice in valid_choices]
    logger.debug(f'category_choice: {category_choice}')

    # フィルタ処理
    if category_choice:
        q = Q()
        for category in category_choice:
            q |= Q(category_choice__icontains=category)
        threads = Thread.objects.filter(q)
    else:
        threads = Thread.objects.all()

    # フリーワード検索用
    search_str = request.GET.get("search_str", "")
    logger.debug(f'Searching for: {search_str}')
    if search_str:
        object_list = threads.filter(
            Q(name__icontains=search_str) |
            Q(overview__icontains=search_str) |
            Q(context__icontains=search_str) |
            Q(remarks__icontains=search_str)
        )
    else:
        object_list = threads

    # 並び替え処理
    sort_options = {
        "name_asc": "name",
        "name_desc": "-name",
        "created_asc": "created_at",
        "created_desc": "-created_at",
        "updated_asc": "updated_at",
        "updated_desc": "-updated_at",
    }
    sort_by = request.GET.get("sort_by", "name_asc")
    logger.debug(f'Sort by: {sort_by}')
    sort_field = sort_options.get(sort_by, "-id")  # デフォルトは -id
    object_list = object_list.order_by(sort_field)

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

    context = {
        'display_object_list': display_object_list,
        'link_object_list': link_object_list,
        'search_category_choice': search_category_choice,
        'search_str': search_str,
        'sort_by': sort_by,
    }

    context.update({'CATEGORY_CHOICES': Thread.CATEGORY_CHOICES})

    logger.info('return render thread/list.html')
    return render(request, 'thread/list.html', context)


def detail_view(request, pk):
    logger.info('start Thread detail_view')

    logger.debug('get Thread object(pk)')
    object = get_object_or_404(Thread, pk=pk)

    # 所属しているすべてのグループを取得
    joined_profiles = object.get_profiles

    # 該当Threadのchat一覧取得(ページング機能付き)
    logger.debug('start Thread Chat list_view')

    page_size = 40 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    object_list = ThreadChat.objects.filter(thread=object).order_by('-order_by_at').all()  # order_by_at の降順で取得
    
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


    context = {'object': object, 'joined_profiles': joined_profiles,
               'display_object_list': display_object_list, 'link_object_list': link_object_list}

    context.update({'CATEGORY_CHOICES': Thread.CATEGORY_CHOICES})

    logger.debug('return render thread/detail.html')
    return render(request, 'thread/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Thread create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = ThreadForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Thread form.is_valid')

            name_data = form.cleaned_data['name']

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')

            category_choice_data = form.cleaned_data['category_choice']            
            overview_data = form.cleaned_data['overview']
            context_data = form.cleaned_data['context']
            remarks_data = form.cleaned_data['remarks']
            pic_data = request.user.profile

            try:
                object = Thread.objects.create(
                    name = name_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    category_choice = category_choice_data,
                    overview = overview_data,
                    context = context_data,
                    remarks = remarks_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Thread object: {e}')
                logger.info('return render thread/create.html')
                return render(request, 'thread/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                object.images = create_images(object, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                object.themes = create_themes(object, themes_data)

            try:
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data in Thread object: {e}')

            logger.info('return redirect thread:list')
            return redirect('thread:list')
        else:
            logger.error('form is invalid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = ThreadForm()
        context = {'form': form}
    
    context.update({'CATEGORY_CHOICES': Thread.CATEGORY_CHOICES})

    logger.info('return render thread/create.html')
    return render(request, 'thread/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Thread update_view')

    logger.debug('get Thread object(pk)')
    object = get_object_or_404(Thread, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = ThreadForm(request.POST, request.FILES)
        context = {'object': object, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            object.name = form.cleaned_data['name']
            object.category_choice = form.cleaned_data['category_choice']
            object.overview = form.cleaned_data['overview']
            object.context = form.cleaned_data['context']
            object.remarks = form.cleaned_data['remarks']
            object.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')

            if images_data: # File Selected
                logger.debug('images_data exists')
                object.images = update_images(object, images_data)

            if themes_data: # File Selected
                logger.debug(f'themes_data exists={themes_data}')
                object.themes = update_themes(object, themes_data)

            try:
                logger.debug('save updated Thread object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the Thread object: {e}')

            logger.info('return redirect thread:list')
            return redirect('thread:list')
        else:
            logger.error('form not is_valid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = ThreadForm(instance=object) # putback the form
        context = {'object': object, 'form': form}
    
    context.update({'CATEGORY_CHOICES': Thread.CATEGORY_CHOICES})

    logger.info('return render thread/update.html')
    return render(request, 'thread/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Thread delete_view')

    logger.debug('get Thread object(pk)')
    object = get_object_or_404(Thread, pk=pk)
    context = {'object': object}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if object.images:
            logger.debug('old images_data exists')
            object = delete_images(object)

        # **古いファイルを削除**
        if object.themes:
            logger.debug('old themes_data exists')
            object = delete_themes(object)

        try:
            logger.debug('delete old Thread object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete Thread object: {e}')

        logger.info('return redirect thread:list')
        return redirect('thread:list')
    else:
        logger.info('GET method')
    
    context.update({'CATEGORY_CHOICES': Thread.CATEGORY_CHOICES})

    logger.info('return render thread/delete.html')
    return render(request, 'thread/delete.html', context)

@login_required
def disp_qr_view(request, pk):
    logger.info('start Friend disp_qr_view')

    base_url = f"{settings.SITE_DOMAIN}/thread/join/?thread_id="  # 実際のドメインに要変更
    url_for_qr = f"{base_url}{pk}"
    logger.info(f'url_for_qr={ url_for_qr }')
    
    return disp_qr_code(url_for_qr)

@login_required
def join_view(request):
    logger.info('start Thread join_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # thread_with = Thread target
    try:
        thread_id = int(request.GET.get("thread_id", 1)) # get profile_id from URL query
        logger.debug(f'thread_id={thread_id}')
        thread_with = Thread.objects.get(id=thread_id)
    except ValueError:
        logger.debug(f'couldnt catch target thread_with_id={thread_with_id}')
        thread_id = 1

    context = {'profile_own': profile_own, 'thread_with': thread_with}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報から2つのProfileを取得(ACCEPTを押下されたもののみ)
        thread_with_id = request.POST["thread_with_id"]
        logger.debug(f'POST thread_with_id={thread_with_id}')
        thread = get_object_or_404(Thread, id=thread_with_id)
        logger.debug(f'POST thread={thread}')

        try:
            # ThreadにProfileを登録
            profile_own.threads.add(thread)
            profile_own.save()
        except Exception as e:
            logger.error(f'couldnt create thread-profile object thread_id={thread.id} profile_id={profile_own.id}: {e}')

        logger.info('return redirect thread:detail')
        return redirect('thread:detail', thread.id)
    else:
        logger.info('GET method')
        pass

    logger.info('return render thread/join.html')
    return render(request, 'thread/join.html', context)

@login_required
def leave_view(request, pk):
    logger.info('start Thread leave_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # thread_with = Thread target
    try:
        thread_with = Thread.objects.get(pk=pk)
    except ValueError:
        logger.debug(f'couldnt catch target thread_with={thread_with}')

    context = {'profile_own': profile_own, 'thread_with': thread_with}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報から2つのProfileを取得(ACCEPTを押下されたもののみ)
        thread_with_id = request.POST["thread_with_id"]
        logger.debug(f'POST thread_with_id={thread_with_id}')
        thread = get_object_or_404(Thread, id=thread_with_id)
        logger.debug(f'POST thread={thread}')

        try:
            # ThreadにProfileを登録
            profile_own.threads.remove(thread)
            profile_own.save()
        except Exception as e:
            logger.error(f'couldnt remove thread-profile object thread_id={thread.id} profile_id={profile_own.id}: {e}')

        logger.info('return redirect thread:list')
        return redirect('thread:list')
    else:
        logger.info('GET method')
        pass

    logger.info('return render thread/leave.html')
    return render(request, 'thread/leave.html', context)

@csrf_exempt  # 関数デコレータに変更
@login_required
def push_likes(request, pk):
    logger.info('start Thread push_likes')

    if request.method == 'POST':
        logger.info('POST method')

        thread = get_object_or_404(Thread, id=pk)
        logger.debug(f'get Thread object(pk)={thread}')

        # いいね処理を実行
        thread.push_likes(request)

        # Ajaxにいいね数を返す
        logger.info(f'return likes:({thread.likes})')
        return JsonResponse({'likes': f'({thread.likes})'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)


def chat_list_view(request):
    logger.debug('start Thread Chat list_view')

    page_size = 40 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    object_list = ThreadChat.objects.order_by('-order_by_at').all()  # order_by_at の降順で取得
    
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

    logger.info('return render thread/chat/list.html')
    return render(request, 'thread/chat/list.html', context)


def chat_detail_view(request, pk):
    logger.info('start Thread Chat detail_view')

    logger.debug('get ThreadChat object(pk)')
    object = get_object_or_404(ThreadChat, pk=pk)

    context = {'object': object}

    logger.debug('return render thread/chat/detail.html')
    return render(request, 'thread/chat/detail.html', context)


@login_required
def chat_create_view(request, thread_pk):
    logger.info('start Thread Chat create_view')

    logger.debug('get Thread object(pk)')
    thread_object = get_object_or_404(Thread, pk=thread_pk)

    if request.method == "POST":
        logger.info('POST method')

        form = ThreadChatForm(request.POST, request.FILES)
        context = {'thread_object': thread_object, 'form': form}

        if form.is_valid():
            logger.debug('ThreadChat form.is_valid')

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
                object = ThreadChat.objects.create(
                    title = title_data,
                    context = context_data,
                    author = author_data,
                    profile = profile_data,
                    images = None, # 画像はまだ保存しない
                    created_pic = pic_data,
                    updated_pic = pic_data,
                    thread = thread_object,
                )
            except Exception as e:
                logger.error(f'couldnt create the ThreadChat object: {e}')
                logger.info('return render thread/chat/create.html')
                return render(request, 'thread/chat/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                object.images = create_images(object, images_data)

                try:
                    logger.debug('save new images_data')
                    object.save()
                except:
                    logger.error(f'couldnt save the images_data in ThreadChat object: {e}')

            logger.info('return redirect thread:detail')
            return redirect('thread:detail', object.thread.id )
        else:
            logger.error('form is invalid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = ThreadChatForm()
        context = {'thread_object': thread_object, 'form': form}
    
    logger.info('return render thread/chat/create.html')
    return render(request, 'thread/chat/create.html', context)
    

@login_required
def chat_update_view(request, pk):
    logger.info('start Thread Chat update_view')

    logger.debug('get ThreadChat object(pk)')
    object = get_object_or_404(ThreadChat, pk=pk)
    callback_thread = object.thread
    
    if request.method == "POST":
        logger.info('POST method')

        form = ThreadChatForm(request.POST, request.FILES)
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
                logger.debug('save updated ThreadChat object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the ThreadChat object: {e}')

            logger.info('return redirect thread:detail')
            return redirect('thread:detail', callback_thread.id )
        else:
            logger.error('form not is_valid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = ThreadChatForm(instance=object) # putback the form
        context = {'object': object, 'form': form}
    
    logger.info('return render thread/chat/update.html')
    return render(request, 'thread/chat/update.html', context)


@login_required
def chat_delete_view(request, pk):
    logger.info('start Thread Chat delete_view')

    logger.debug('get ThreadChat object(pk)')
    object = get_object_or_404(ThreadChat, pk=pk)
    callback_thread = object.thread
    context = {'object': object}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if object.images:
            delete_images(object)
        
        try:
            logger.debug('delete old ThreadChat object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete ThreadChat object: {e}')

        logger.info('return redirect thread:chat_list')
        return redirect('thread:detail', callback_thread.id )
    else:
        logger.info('GET method')
    
    logger.info('return render thread/chat/delete.html')
    return render(request, 'thread/chat/delete.html', context)

@csrf_exempt  # 関数デコレータに変更
@login_required
def chat_push_likes(request, pk):
    logger.info('start Thread Chat push_likes')

    if request.method == 'POST':
        logger.info('POST method')

        threadchat = get_object_or_404(ThreadChat, id=pk)
        logger.debug(f'get ThreadChat object(pk)={threadchat}')

        # いいね処理を実行
        threadchat.push_likes(request)

        # Ajaxにいいね数を返す
        logger.info(f'return likes:({threadchat.likes})')
        return JsonResponse({'likes': f'({threadchat.likes})'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt  # 関数デコレータに変更
@login_required
def chat_age_order_by_at(request, pk):
    logger.info('start Thread Chat age_order_by_at')

    if request.method == 'POST':
        logger.info('POST method')

        threadchat = get_object_or_404(ThreadChat, id=pk)
        logger.debug(f'get ThreadChat object(pk)={threadchat}')

        # アゲ処理を実行
        threadchat.age_order_by_at(request)

        # Ajaxにいいね数を返す
        logger.info('return True')
        return JsonResponse({'status': 'True'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)
