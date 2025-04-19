from django.conf import settings
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes, create_files, update_files, delete_files, safe_json_post
from .models import SharedFile
from .forms  import SharedFileForm
from user.models import Profile

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page=1):
    logger.debug('start SharedFile list_view')

    PAGE_SIZE = 12 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    # カテゴリ検索
    search_category_choice = request.GET.getlist('search_category_choice')
    logger.debug(f'search_category_choice: {search_category_choice}')
    # 選択肢のバリデーション
    valid_choices = [choice[0] for choice in SharedFile.CATEGORY_CHOICES]
    logger.debug(f'valid_choices: {valid_choices}')
    category_choice = [choice for choice in search_category_choice if choice in valid_choices]
    logger.debug(f'category_choice: {category_choice}')

    # フィルタ処理
    if category_choice:
        q = Q()
        for category in category_choice:
            q |= Q(category_choice__icontains=category)
        object_list = SharedFile.objects.filter(q)
    else:
        object_list = SharedFile.objects.all()

    # フリーワード検索用
    search_str = request.GET.get("search_str", "")
    logger.debug(f'Searching for: {search_str}')
    if search_str:
        object_list = object_list.filter(
            Q(title__icontains=search_str) |
            Q(overview__icontains=search_str) |
            Q(context__icontains=search_str) |
            Q(remarks__icontains=search_str)
        )

    # 並び替え処理
    sort_options = {
        "likes_desc": "-likes",
        "likes_asc": "likes",
        "updated_desc": "-updated_at",
        "updated_asc": "updated_at",
        "title_asc": "title",
        "title_desc": "-title",
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
        'search_category_choice': search_category_choice,
        'search_str': search_str,
        'sort_by': sort_by,
    }

    context.update({'CATEGORY_CHOICES': SharedFile.CATEGORY_CHOICES})

    logger.info('return render sharedfile/list.html')
    return render(request, 'sharedfile/list.html', context)


def detail_view(request, pk):
    logger.info('start SharedFile detail_view')

    logger.debug('get SharedFile object(pk)')
    sharedfile = get_object_or_404(SharedFile, pk=pk)

    context = {'object': sharedfile}

    context.update({'CATEGORY_CHOICES': SharedFile.CATEGORY_CHOICES})

    logger.debug('return render sharedfile/detail.html')
    return render(request, 'sharedfile/detail.html', context)


@login_required
def create_view(request):
    logger.info('start SharedFile create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = SharedFileForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('SharedFile form.is_valid')

            title_data = form.cleaned_data['title']

            images_data = request.FILES.get('images')
            themes_data = request.FILES.get('themes')
            files_data = request.FILES.get('files')

            category_choice_data = form.cleaned_data['category_choice']            
            overview_data = form.cleaned_data['overview']
            context_data = form.cleaned_data['context']
            remarks_data = form.cleaned_data['remarks']
            pic_data = request.user.profile

            try:
                sharedfile = SharedFile.objects.create(
                    title = title_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    category_choice = category_choice_data,
                    files = None, # ファイルはまだ保存しない
                    overview = overview_data,
                    context = context_data,
                    remarks = remarks_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the SharedFile object: {e}')
                logger.info('return render sharedfile/create.html')
                return render(request, 'sharedfile/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                sharedfile.images = create_images(sharedfile, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                sharedfile.themes = create_themes(sharedfile, themes_data)

            if files_data:
                logger.debug('images_data exists')
                sharedfile.files = create_files(sharedfile, files_data)

            try:
                sharedfile.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data / files_data in SharedFile object: {e}')

            logger.info('return redirect sharedfile:list')
            return redirect('sharedfile:list')
        else:
            logger.error('form is invalid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = SharedFileForm()
        context = {'form': form}
    
    context.update({'CATEGORY_CHOICES': SharedFile.CATEGORY_CHOICES})

    logger.info('return render sharedfile/create.html')
    return render(request, 'sharedfile/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start SharedFile update_view')

    logger.debug('get SharedFile object(pk)')
    sharedfile = get_object_or_404(SharedFile, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = SharedFileForm(request.POST, request.FILES)
        context = {'object': sharedfile, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            sharedfile.title = form.cleaned_data['title']
            sharedfile.category_choice = form.cleaned_data['category_choice']
            sharedfile.overview = form.cleaned_data['overview']
            sharedfile.context = form.cleaned_data['context']
            sharedfile.remarks = form.cleaned_data['remarks']
            sharedfile.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            delete_images_flg = form.cleaned_data.get('delete_images_flg')
            themes_data = request.FILES.get('themes')
            delete_themes_flg = form.cleaned_data.get('delete_themes_flg')
            files_data = request.FILES.get('files')

            if images_data: # File Selected
                logger.debug('images_data exists')
                sharedfile.images = update_images(sharedfile, images_data)
            elif delete_images_flg and sharedfile.images:
                logger.debug('delete_images exists')
                delete_images(sharedfile)
                sharedfile.images = None

            if themes_data: # File Selected
                logger.debug(f'themes_data exists={themes_data}')
                sharedfile.themes = update_themes(sharedfile, themes_data)
            elif delete_themes_flg and sharedfile.themes:
                logger.debug('delete_themes exists')
                delete_themes(sharedfile)
                sharedfile.themes = None

            if files_data: # File Selected
                logger.debug(f'files_data exists={files_data}')
                sharedfile.files = update_files(sharedfile, files_data)

            try:
                logger.debug('save updated SharedFile object')
                sharedfile.save()
            except Exception as e:
                logger.error(f'couldnt save the SharedFile object: {e}')

            logger.info('return redirect sharedfile:list')
            return redirect('sharedfile:list')
        else:
            logger.error('form not is_valid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = SharedFileForm(instance=sharedfile) # putback the form
        context = {'object': sharedfile, 'form': form}
    
    context.update({'CATEGORY_CHOICES': SharedFile.CATEGORY_CHOICES})

    logger.info('return render sharedfile/update.html')
    return render(request, 'sharedfile/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start SharedFile delete_view')

    logger.debug('get SharedFile object(pk)')
    sharedfile = get_object_or_404(SharedFile, pk=pk)
    context = {'object': sharedfile}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if sharedfile.images:
            logger.debug('old images_data exists')
            sharedfile = delete_images(sharedfile)

        # **古いファイルを削除**
        if sharedfile.themes:
            logger.debug('old themes_data exists')
            sharedfile = delete_themes(sharedfile)

        # **古いファイルを削除**
        if sharedfile.files:
            logger.debug('old files_data exists')
            sharedfile = delete_files(sharedfile)

        try:
            logger.debug('delete old SharedFile object')
            sharedfile.delete()
        except Exception as e:
            logger.error(f'couldnt delete SharedFile object: {e}')

        logger.info('return redirect sharedfile:list')
        return redirect('sharedfile:list')
    else:
        logger.info('GET method')
    
    context.update({'CATEGORY_CHOICES': SharedFile.CATEGORY_CHOICES})

    logger.info('return render sharedfile/delete.html')
    return render(request, 'sharedfile/delete.html', context)

@login_required
def push_likes(request, pk):
    logger.info('start SharedFile push_likes')
    return safe_json_post(request, lambda: _push_likes_logic(request, pk))

def _push_likes_logic(request, pk):
    sharedfile = get_object_or_404(SharedFile, id=pk)
    logger.debug(f'get SharedFile object(pk)={sharedfile}')

    sharedfile.push_likes(request)

    logger.info(f'return likes:{sharedfile.likes}')
    return JsonResponse({'likes': f'({sharedfile.likes})'})
