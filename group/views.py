from django.conf import settings
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import disp_qr_code
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes, safe_json_post
from .models import Group
from .forms  import GroupForm
from user.models import Profile

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request):
    logger.debug('start Group list_view')

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
    valid_choices = [choice[0] for choice in Group.CATEGORY_CHOICES]
    logger.debug(f'valid_choices: {valid_choices}')
    category_choice = [choice for choice in search_category_choice if choice in valid_choices]
    logger.debug(f'category_choice: {category_choice}')

    # フィルタ処理
    if category_choice:
        q = Q()
        for category in category_choice:
            q |= Q(category_choice__icontains=category)
        object_list = Group.objects.filter(q)
    else:
        object_list = Group.objects.all()

    # フリーワード検索用
    search_str = request.GET.get("search_str", "")
    logger.debug(f'Searching for: {search_str}')
    if search_str:
        object_list = object_list.filter(
            Q(name__icontains=search_str) |
            Q(context__icontains=search_str) |
            Q(remarks__icontains=search_str)
        )

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
        'search_category_choice': search_category_choice,
        'search_str': search_str,
        'sort_by': sort_by,
    }

    context.update({'CATEGORY_CHOICES': Group.CATEGORY_CHOICES})

    logger.info('return render group/list.html')
    return render(request, 'group/list.html', context)


def detail_view(request, pk):
    logger.info('start Group detail_view')

    logger.debug('get Group object(pk)')
    group = get_object_or_404(Group, pk=pk)

    # 所属しているすべてのグループを取得
    joined_profiles = group.get_profiles

    context = {'object': group, 'joined_profiles': joined_profiles}

    context.update({'CATEGORY_CHOICES': Group.CATEGORY_CHOICES})

    logger.debug('return render group/detail.html')
    return render(request, 'group/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Group create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = GroupForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Group form.is_valid')

            name_data = form.cleaned_data['name']

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')

            category_choice_data = form.cleaned_data['category_choice']
            context_data = form.cleaned_data['context']
            remarks_data = form.cleaned_data['remarks']
            schedule_monthly_data = form.cleaned_data['schedule_monthly']
            schedule_weekly_data = form.cleaned_data['schedule_weekly']
            task_control_data = form.cleaned_data['task_control']
            pic_data = request.user.profile

            try:
                group = Group.objects.create(
                    name = name_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    category_choice = category_choice_data,
                    context = context_data,
                    remarks = remarks_data,
                    schedule_monthly = schedule_monthly_data,
                    schedule_weekly = schedule_weekly_data,
                    task_control = task_control_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Group object: {e}')
                logger.info('return render group/create.html')
                return render(request, 'group/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                group.images = create_images(group, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                group.themes = create_themes(group, themes_data)

            try:
                group.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data in Group object: {e}')

            logger.info('return redirect group:list')
            return redirect('group:list')
        else:
            logger.error('form is invalid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = GroupForm()
        context = {'form': form}
    
    context.update({'CATEGORY_CHOICES': Group.CATEGORY_CHOICES})

    logger.info('return render group/create.html')
    return render(request, 'group/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Group update_view')

    logger.debug('get Group object(pk)')
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = GroupForm(request.POST, request.FILES)
        context = {'object': group, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            group.name = form.cleaned_data['name']
            group.category_choice = form.cleaned_data['category_choice']
            group.context = form.cleaned_data['context']
            group.remarks = form.cleaned_data['remarks']
            group.schedule_monthly = form.cleaned_data['schedule_monthly']
            group.schedule_weekly = form.cleaned_data['schedule_weekly']
            group.task_control = form.cleaned_data['task_control']
            group.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            delete_images_flg = form.cleaned_data.get('delete_images_flg')
            themes_data = request.FILES.get('themes')
            delete_themes_flg = form.cleaned_data.get('delete_themes_flg')

            if images_data: # File Selected
                logger.debug('images_data exists')
                group.images = update_images(group, images_data)
            elif delete_images_flg and group.images:
                logger.debug('delete_images exists')
                delete_images(group)
                group.images = None
            
            if themes_data: # File Selected
                logger.debug(f'themes_data exists={themes_data}')
                group.themes = update_themes(group, themes_data)
            elif delete_themes_flg and group.themes:
                logger.debug('delete_themes exists')
                delete_themes(group)
                group.themes = None

            try:
                logger.debug('save updated Group object')
                group.save()
            except Exception as e:
                logger.error(f'couldnt save the Group object: {e}')

            logger.info('return redirect group:list')
            return redirect('group:list')
        else:
            logger.error('form not is_valid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = GroupForm(instance=group) # putback the form
        context = {'object': group, 'form': form}
    
    context.update({'CATEGORY_CHOICES': Group.CATEGORY_CHOICES})

    logger.info('return render group/update.html')
    return render(request, 'group/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Group delete_view')

    logger.debug('get Group object(pk)')
    group = get_object_or_404(Group, pk=pk)
    context = {'object': group}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if group.images:
            logger.debug('old images_data exists')
            group = delete_images(group)

        # **古いファイルを削除**
        if group.themes:
            logger.debug('old themes_data exists')
            group = delete_themes(group)

        try:
            logger.debug('delete old Group object')
            group.delete()
        except Exception as e:
            logger.error(f'couldnt delete Group object: {e}')

        logger.info('return redirect group:list')
        return redirect('group:list')
    else:
        logger.info('GET method')
    
    context.update({'CATEGORY_CHOICES': Group.CATEGORY_CHOICES})

    logger.info('return render group/delete.html')
    return render(request, 'group/delete.html', context)

@login_required
def disp_qr_view(request, pk):
    logger.info('start Group join disp_qr_view')

    base_url = f"{settings.SITE_DOMAIN}/group/join/?group_id="  # 実際のドメインに要変更
    url_for_qr = f"{base_url}{pk}"
    logger.info(f'url_for_qr={ url_for_qr }')
    
    return disp_qr_code(url_for_qr)

@login_required
def join_view(request):
    logger.info('start Group join_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # group_with = Group target
    try:
        group_id = int(request.GET.get("group_id", 1)) # get profile_id from URL query
        logger.debug(f'group_id={group_id}')
        group_with = Group.objects.get(id=group_id)
    except ValueError:
        logger.debug(f'couldnt catch target group_with_id={group_with_id}')
        group_id = 1

    context = {'profile_own': profile_own, 'group_with': group_with}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報から2つのProfileを取得(ACCEPTを押下されたもののみ)
        group_with_id = request.POST["group_with_id"]
        logger.debug(f'POST group_with_id={group_with_id}')
        group = get_object_or_404(Group, id=group_with_id)
        logger.debug(f'POST group={group}')

        try:
            # GroupにProfileを登録
            profile_own.groups.add(group)
            profile_own.save()
        except Exception as e:
            logger.error(f'couldnt create group-profile object group_id={group.id} profile_id={profile_own.id}: {e}')

        logger.info('return redirect group:detail')
        return redirect('group:detail', group.id)
    else:
        logger.info('GET method')
        pass

    logger.info('return render group/join.html')
    return render(request, 'group/join.html', context)

@login_required
def leave_view(request, pk):
    logger.info('start Group leave_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # group_with = Group target
    try:
        group_with = Group.objects.get(pk=pk)
    except ValueError:
        logger.debug(f'couldnt catch target group_with={group_with}')

    context = {'profile_own': profile_own, 'group_with': group_with}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報から2つのProfileを取得(ACCEPTを押下されたもののみ)
        group_with_id = request.POST["group_with_id"]
        logger.debug(f'POST group_with_id={group_with_id}')
        group = get_object_or_404(Group, id=group_with_id)
        logger.debug(f'POST group={group}')

        try:
            # GroupにProfileを登録
            profile_own.groups.remove(group)
            profile_own.save()
        except Exception as e:
            logger.error(f'couldnt remove group-profile object group_id={group.id} profile_id={profile_own.id}: {e}')

        logger.info('return redirect group:list')
        return redirect('group:list')
    else:
        logger.info('GET method')
        pass

    logger.info('return render group/leave.html')
    return render(request, 'group/leave.html', context)

@login_required
def push_likes(request, pk):
    logger.info('start Group push_likes')
    return safe_json_post(request, lambda: _push_likes_logic(request, pk))

def _push_likes_logic(request, pk):
    group = get_object_or_404(Group, id=pk)
    logger.debug(f'get Group object(pk)={group}')

    group.push_likes(request)

    logger.info(f'return likes:{group.likes}')
    return JsonResponse({'likes': f'({group.likes})'})
