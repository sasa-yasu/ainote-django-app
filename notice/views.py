import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images
from .models import Notice
from .forms  import NoticeForm

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page=1):
    logger.debug('start Notice list_view')

    PAGE_SIZE = 12 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    object_list = Notice.objects.order_by('published_at') 

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

    logger.info('return render notice/list.html')
    return render(request, 'notice/list.html', context)


def detail_view(request, pk):
    logger.info('start Notice detail_view')

    logger.debug('get Notice object(pk)')
    notice = get_object_or_404(Notice, pk=pk)

    context = {'object': notice}

    logger.debug('return render notice/detail.html')
    return render(request, 'notice/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Notice create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = NoticeForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Notice form.is_valid')

            images_data = request.FILES.get("images")
            
            title_data = form.cleaned_data['title']
            period_data = form.cleaned_data['period']
            overview_data = form.cleaned_data['overview']
            context_data = form.cleaned_data['context']
            published_at_data = form.cleaned_data['published_at']
            remarks_data = form.cleaned_data['remarks']
            pic_data = request.user.profile

            try:
                notice = Notice.objects.create(
                    images = None, # 画像はまだ保存しない
                    title = title_data,
                    period = period_data,
                    overview = overview_data,
                    context = context_data,
                    published_at = published_at_data,
                    remarks = remarks_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Notice object: {e}')
                logger.info('return render notice/create.html')
                return render(request, 'notice/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                notice.images = create_images(notice, images_data)

                try:
                    notice.save()
                except:
                    logger.error(f'couldnt save the images_data in Notice object: {e}')

            logger.info('return redirect notice:list')
            return redirect('notice:list')
        else:
            logger.error('form is invalid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = NoticeForm()
        context = {'form': form}
    
    logger.info('return render notice/create.html')
    return render(request, 'notice/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Notice update_view')

    logger.debug('get Notice object(pk)')
    notice = get_object_or_404(Notice, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = NoticeForm(request.POST, request.FILES)
        context = {'object': notice, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            notice.title = form.cleaned_data['title']
            notice.period = form.cleaned_data['period']
            notice.overview = form.cleaned_data['overview']
            notice.context = form.cleaned_data['context']
            notice.published_at = form.cleaned_data['published_at']
            notice.remarks = form.cleaned_data['remarks']
            notice.updated_pic = request.user.profile

            images_data = request.FILES.get("images")

            if images_data: # File Selected
                logger.debug('images_data exists')                
                notice.images = update_images(notice, images_data)

            try:
                logger.debug('save updated Notice object')
                notice.save()
            except Exception as e:
                logger.error(f'couldnt save the Notice object: {e}')

            logger.info('return redirect notice:list')
            return redirect('notice:list')
        else:
            logger.error('form not is_valid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = NoticeForm(instance=notice) # putback the form
        context = {'object': notice, 'form': form}
    
    logger.info('return render notice/update.html')
    return render(request, 'notice/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Notice delete_view')

    logger.debug('get Notice object(pk)')
    notice = get_object_or_404(Notice, pk=pk)
    context = {'object': notice}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if notice.images:
            delete_images(notice)

        try:
            logger.debug('delete old Notice object')
            notice.delete()
        except Exception as e:
            logger.error(f'couldnt delete Notice object: {e}')

        logger.info('return redirect notice:list')
        return redirect('notice:list')
    else:
        logger.info('GET method')
    
    logger.info('return render notice/delete.html')
    return render(request, 'notice/delete.html', context)
