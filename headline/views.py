import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images
from .models import Headline
from .forms  import HeadlineForm

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page=1):
    logger.debug('start Headline list_view')

    PAGE_SIZE = 12 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    object_list = Headline.objects.order_by('published_at')

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

    logger.info('return render headline/list.html')
    return render(request, 'headline/list.html', context)


def detail_view(request, pk):
    logger.info('start Headline detail_view')

    logger.debug('get Headline object(pk)')
    headline = get_object_or_404(Headline, pk=pk)

    context = {'object': headline}

    logger.debug('return render headline/detail.html')
    return render(request, 'headline/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Headline create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = HeadlineForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Headline form.is_valid')

            title_data = form.cleaned_data['title']

            images_data = request.FILES.get("images")
            
            period_data = form.cleaned_data['period']
            overview_data = form.cleaned_data['overview']
            context_data = form.cleaned_data['context']
            published_at_data = form.cleaned_data['published_at']
            remarks_data = form.cleaned_data['remarks']
            pic_data = request.user.profile

            try:
                headline = Headline.objects.create(
                    title = title_data,
                    period = period_data,
                    overview = overview_data,
                    context = context_data,
                    published_at = published_at_data,
                    remarks = remarks_data,
                    images = None, # 画像はまだ保存しない
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Headline object: {e}')
                logger.info('return render headline/create.html')
                return render(request, 'headline/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                headline.images = create_images(headline, images_data)

                try:
                    headline.save()
                except:
                    logger.error(f'couldnt save the images_data in Headline object: {e}')

            logger.info('return redirect headline:list')
            return redirect('headline:list')
        else:
            logger.error('form is invalid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = HeadlineForm()
        context = {'form': form}
    
    logger.info('return render headline/create.html')
    return render(request, 'headline/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Headline update_view')

    logger.debug('get Headline object(pk)')
    headline = get_object_or_404(Headline, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = HeadlineForm(request.POST, request.FILES)
        context = {'object': headline, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            headline.title = form.cleaned_data['title']
            headline.period = form.cleaned_data['period']
            headline.overview = form.cleaned_data['overview']
            headline.context = form.cleaned_data['context']
            headline.published_at = form.cleaned_data['published_at']
            headline.remarks = form.cleaned_data['remarks']
            headline.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            
            if images_data: # File Selected
                logger.debug('images_data exists')                
                headline.images = update_images(headline, images_data)

            try:
                logger.debug('save updated Headline object')
                headline.save()
            except Exception as e:
                logger.error(f'couldnt save the Headline object: {e}')

            logger.info('return redirect headline:list')
            return redirect('headline:list')
        else:
            logger.error('form not is_valid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = HeadlineForm(instance=headline) # putback the form
        context = {'object': headline, 'form': form}
    
    logger.info('return render headline/update.html')
    return render(request, 'headline/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Headline delete_view')

    logger.debug('get Headline object(pk)')
    headline = get_object_or_404(Headline, pk=pk)
    context = {'object': headline}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if headline.images:
            delete_images(headline)

        try:
            logger.debug('delete old Headline object')
            headline.delete()
        except Exception as e:
            logger.error(f'couldnt delete Headline object: {e}')

        logger.info('return redirect headline:list')
        return redirect('headline:list')
    else:
        logger.info('GET method')
    
    logger.info('return render headline/delete.html')
    return render(request, 'headline/delete.html', context)
