import os
import logging
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from .models import Headline
from .forms  import HeadlineForm

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page_cnt=1):
    logger.debug('start Headline list_view')

    page_size = 12 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    object_list = Headline.objects.order_by('published_at').all() 

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

    logger.info('return render headline/list.html')
    return render(request, 'headline/list.html', context)


def detail_view(request, pk):
    logger.info('start Headline detail_view')

    logger.debug('get Headline object(pk)')
    object = get_object_or_404(Headline, pk=pk)

    context = {'object': object}

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

            try:
                object = Headline.objects.create(
                    title = title_data,
                    period = period_data,
                    overview = overview_data,
                    context = context_data,
                    published_at = published_at_data,
                    remarks = remarks_data,
                    images = None, # 画像はまだ保存しない
                )
            except Exception as e:
                logger.error(f'couldnt create the Headline object: {e}')
                logger.info('return render headline/create.html')
                return render(request, 'headline/create.html', {'form': form})

            if images_data:
                logger.debug('images_data exists')
                ext = os.path.splitext(images_data.name)[1]  # 拡張子を取得
                timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                images_data.name = f"{object.id}_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                logger.debug(f'images_data={images_data}')
                object.images = images_data

                try:
                    object.save()
                except:
                    logger.error(f'couldnt save the images_data in Headline object: {e}')

            logger.info('return redirect headline:list')
            return redirect('headline:list')
        else:
            logger.error('form is invalid.')
            print(form.errors)  # エラー内容をログに出力
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
    object = get_object_or_404(Headline, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = HeadlineForm(request.POST, request.FILES)
        context = {'object': object, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            object.title = form.cleaned_data['title']
            object.period = form.cleaned_data['period']
            object.overview = form.cleaned_data['overview']
            object.context = form.cleaned_data['context']
            object.published_at = form.cleaned_data['published_at']
            object.remarks = form.cleaned_data['remarks']

            images_data = request.FILES.get("images")
            
            # images data handling start
            if images_data: # File Selected
                logger.debug('images_data exists')
                
                # **古いファイルを削除**
                if object.images:
                    logger.debug('old images_data exists')
                    old_image_path = object.images.path  # 旧ファイルのパス
                    logger.debug(f'old images_data={old_image_path}')
                    if default_storage.exists(old_image_path):
                        logger.debug('old images_data file exists')
                        try:
                            logger.debug('delete old images_data')
                            default_storage.delete(old_image_path)  # 削除
                        except Exception as e:
                            logger.error(f'couldnt delete old images_data={old_image_path}: {e}')
                    else:
                        logger.debug('old images_data file not exists')
                # **新しいファイルを保存**
                ext = os.path.splitext(images_data.name)[1]  # 拡張子を取得
                timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                images_data.name = f"{object.id}_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                logger.debug(f'new images_data={images_data}')
                logger.debug('save new images_data')
                object.images = images_data
            # images data handling end

            try:
                logger.debug('save updated Headline object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the Headline object: {e}')

            logger.info('return redirect headline:list')
            return redirect('headline:list')
        else:
            logger.error('form not is_valid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = HeadlineForm(instance=object) # putback the form
        context = {'object': object, 'form': form}
    
    logger.info('return render headline/update.html')
    return render(request, 'headline/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Headline delete_view')

    logger.debug('get Headline object(pk)')
    object = get_object_or_404(Headline, pk=pk)
    context = {'object': object}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if object.images:
            logger.debug('old images_data exists')
            old_image_path = object.images.path  # 旧ファイルのパス
            logger.debug(f'old images_data={old_image_path}')
            if default_storage.exists(old_image_path):
                logger.debug('old images_data file exists')
                try:
                    logger.debug('delete old images_data')
                    default_storage.delete(old_image_path)  # 削除
                except Exception as e:
                    logger.debug(f'couldnt delete old images_data={old_image_path}: {e}')
            else:
                logger.debug('old images_data file not exists')

        try:
            logger.debug('delete old Headline object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete Headline object: {e}')

        logger.info('return redirect headline:list')
        return redirect('headline:list')
    else:
        logger.info('GET method')
    
    logger.info('return render headline/delete.html')
    return render(request, 'headline/delete.html', context)
