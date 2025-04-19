from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes, safe_json_post
from .models import Room
from .forms  import RoomForm
import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page=1):
    logger.debug('start Room list_view')

    PAGE_SIZE = 12 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    # フリーワード検索用
    search_str = request.GET.get("search_str", "")
    logger.debug(f'Searching for: {search_str}')
    if search_str:
        object_list = Room.objects.filter(
            Q(name__icontains=search_str) |
            Q(capacity__icontains=search_str) |
            Q(context__icontains=search_str) |
            Q(remarks__icontains=search_str)
        )
    else:
        object_list = Room.objects.all()

    # 並び替え処理
    sort_options = {
        "likes_desc": "-likes",
        "likes_asc": "likes",
        "updated_desc": "-updated_at",
        "updated_asc": "updated_at",
        "name_asc": "name",
        "name_desc": "-name",
        "created_desc": "-created_at",
        "created_asc": "created_at",
    }
    sort_by = request.GET.get("sort_by", "likes_desc")
    logger.debug(f'Sort by: {sort_by}')
    sort_field = sort_options.get(sort_by, "-id")  # デフォルトは -id
    object_list = object_list.order_by(sort_field)

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

    context = {
        'display_object_list': display_object_list,
        'link_object_list': link_object_list,
        'search_str': search_str,
        'sort_by': sort_by,
    }

    logger.info('return render room/list.html')
    return render(request, 'room/list.html', context)


def detail_view(request, pk):
    logger.info('start Room detail_view')

    logger.debug('get Room object(pk)')
    room = get_object_or_404(Room, pk=pk)

    context = {'object': room}

    logger.debug('return render room/detail.html')
    return render(request, 'room/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Room create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = RoomForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Room form.is_valid')

            name_data = form.cleaned_data['name']
            
            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')
            
            capacity_data = form.cleaned_data['capacity']
            context_data = form.cleaned_data['context']
            remarks_data = form.cleaned_data['remarks']
            schedule_monthly_data = form.cleaned_data['schedule_monthly']
            schedule_weekly_data = form.cleaned_data['schedule_weekly']
            pic_data = request.user.profile

            try:
                room = Room.objects.create(
                    name = name_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    capacity = capacity_data,
                    context = context_data,
                    remarks = remarks_data,
                    schedule_monthly = schedule_monthly_data,
                    schedule_weekly = schedule_weekly_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Room object: {e}')
                logger.info('return render room/create.html')
                return render(request, 'room/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                room.images = create_images(room, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                room.themes = create_themes(room, themes_data)

            try:
                room.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data in Room object: {e}')

            logger.info('return redirect room:list')
            return redirect('room:list')
        else:
            logger.error('form is invalid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = RoomForm()
        context = {'form': form}
    
    logger.info('return render room/create.html')
    return render(request, 'room/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Room update_view')

    logger.debug('get Room object(pk)')
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = RoomForm(request.POST, request.FILES)
        context = {'object': room, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            room.name = form.cleaned_data['name']
            room.capacity = form.cleaned_data['capacity']
            room.context = form.cleaned_data['context']
            room.remarks = form.cleaned_data['remarks']
            room.schedule_monthly = form.cleaned_data['schedule_monthly']
            room.schedule_weekly = form.cleaned_data['schedule_weekly']
            room.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            delete_images_flg = form.cleaned_data.get('delete_images_flg')
            themes_data = request.FILES.get('themes')
            delete_themes_flg = form.cleaned_data.get('delete_themes_flg')

            if images_data: # File Selected
                logger.debug('images_data exists')
                room.images = update_images(room, images_data)
            elif delete_images_flg and room.images:
                logger.debug('delete_images exists')
                delete_images(room)
                room.images = None

            if themes_data: # File Selected
                logger.debug(f'themes_data exists={themes_data}')
                room.themes = update_themes(room, themes_data)
            elif delete_themes_flg and room.themes:
                logger.debug('delete_themes exists')
                delete_themes(room)
                room.themes = None

            try:
                logger.debug('save updated Room object')
                room.save()
            except Exception as e:
                logger.error(f'couldnt save the Room object: {e}')

            logger.info('return redirect room:list')
            return redirect('room:list')
        else:
            logger.error('form not is_valid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = RoomForm(instance=room) # putback the form
        context = {'object': room, 'form': form}
    
    logger.info('return render room/update.html')
    return render(request, 'room/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Room delete_view')

    logger.debug('get Room object(pk)')
    room = get_object_or_404(Room, pk=pk)
    context = {'object': room}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if room.images:
            room = delete_images(room)

        # **古いファイルを削除**
        if room.themes:
            logger.debug('old themes_data exists')
            room = delete_themes(room)

        try:
            logger.debug('delete old Room object')
            room.delete()
        except Exception as e:
            logger.error(f'couldnt delete Room object: {e}')

        logger.info('return redirect room:list')
        return redirect('room:list')
    else:
        logger.info('GET method')
    
    logger.info('return render room/delete.html')
    return render(request, 'room/delete.html', context)

@login_required
def push_likes(request, pk):
    logger.info('start Room push_likes')
    return safe_json_post(request, lambda: _push_likes_logic(request, pk))

def _push_likes_logic(request, pk):
    room = get_object_or_404(Room, id=pk)
    logger.debug(f'get Room object(pk)={room}')

    room.push_likes(request)

    logger.info(f'return likes:{room.likes}')
    return JsonResponse({'likes': f'({room.likes})'})
