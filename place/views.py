import os
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import PlaceForm
from .models import Place, CheckinRecord
from AinoteProject.utils import haversine
from user.models import Profile

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')


def list_view(request, page_cnt=1):
    logger.debug('start Place list_view')

    page_size = 15 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    object_list = Place.objects.order_by('-id').all() 

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

    logger.info('return render place/list.html')
    return render(request, 'place/list.html', context)


def detail_view(request, pk):
    logger.info('start detail_view')

    logger.debug('get Place object(pk)')
    object = get_object_or_404(Place, pk=pk)

    # 現座のログイン状態ログインを取得
    recent_checkin_statuses = object.get_checkin_status

    # 最新の100件のログインを取得
    recent_checkin_records = object.get_checkin_records_by_count(100)

    context = {'object': object, 'recent_checkin_statuses': recent_checkin_statuses, 'recent_checkin_records': recent_checkin_records}

    logger.debug('return render place/detail.html')
    return render(request, 'place/detail.html', context)

@login_required
def create_view(request): 
    logger.info('start Place create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = PlaceForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Place form.is_valid')

            place_data = form.cleaned_data["place"]

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')
            
            area_data = form.cleaned_data["area"]
            overview_data = form.cleaned_data["overview"]
            address_data = form.cleaned_data["address"]
            tel_data = form.cleaned_data["tel"]
            url_data = form.cleaned_data["url"]
            context_data = form.cleaned_data["context"]
            remarks_data = form.cleaned_data["remarks"]
            latitude_data = form.cleaned_data["latitude"]
            longitude_data = form.cleaned_data["longitude"]
            googlemap_url_data = form.cleaned_data["googlemap_url"]

            try:
                object = Place.objects.create(
                    place = place_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    area = area_data,
                    overview = overview_data,
                    address = address_data,
                    tel = tel_data,
                    url = url_data,
                    context = context_data,
                    remarks = remarks_data,
                    latitude = latitude_data,
                    longitude = longitude_data,
                    googlemap_url = googlemap_url_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Place Object: {e}')
                logger.info('return render place/create.html')
                return render(request, 'place/create.html', context)

            if images_data or themes_data:
                if images_data:
                    logger.debug('images_data exists')
                    ext = os.path.splitext(images_data.name)[1]  # 拡張子を取得
                    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                    images_data.name = f"{object.id}_images_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'images_data={images_data}')
                    object.images = images_data

                if themes_data:
                    logger.debug('themes_data exists')
                    ext = os.path.splitext(themes_data.name)[1]  # 拡張子を取得
                    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                    themes_data.name = f"{object.id}_themes_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'themes_data={themes_data}')
                    object.themes = themes_data

                try:
                    object.save()
                except Exception as e:
                    logger.error(f'couldnt save the images_data / themes_data in Place object: {e}')
            
            logger.info('return redirect place:list')
            return redirect('place:list')
        else:
            logger.error('form is invalid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = PlaceForm()
        context = {'form': form}

    logger.info('return render place/create.html')
    return render(request, 'place/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Place update_view')

    logger.debug('get Place object(pk)')
    object = get_object_or_404(Place, pk=pk)

    if request.method == "POST":
        logger.info('POST method')

        form = PlaceForm(request.POST, request.FILES)
        context = {'object': object, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            object.place = form.cleaned_data["place"]
            object.area = form.cleaned_data["area"]
            object.overview = form.cleaned_data["overview"]
            object.address = form.cleaned_data["address"]
            object.tel = form.cleaned_data["tel"]
            object.url = form.cleaned_data["url"]
            object.context = form.cleaned_data["context"]
            object.remarks = form.cleaned_data["remarks"]
            object.latitude = form.cleaned_data["latitude"]
            object.longitude = form.cleaned_data["longitude"]
            object.googlemap_url = form.cleaned_data["googlemap_url"]

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')
            
            if images_data or themes_data:
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
                    images_data.name = f"{object.id}_images_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'new images_data={images_data}')
                    logger.debug('save new images_data')
                    object.images = images_data

                if themes_data: # File Selected
                    logger.debug('themes_data exists')
                    # **古いファイルを削除**
                    if object.themes:
                        logger.debug('old themes_data exists')
                        old_image_path = object.themes.path  # 旧ファイルのパス
                        logger.debug(f'old themes_data={old_image_path}')
                        if default_storage.exists(old_image_path):
                            logger.debug('old themes_data file exists')
                            try:
                                logger.debug('delete old themes_data')
                                default_storage.delete(old_image_path)  # 削除
                            except Exception as e:
                                logger.error(f'couldnt delete old themes_data={old_image_path}: {e}')
                        else:
                            logger.debug('old themes_data file not exists')
                    # **新しいファイルを保存**
                    ext = os.path.splitext(themes_data.name)[1]  # 拡張子を取得
                    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                    themes_data.name = f"{object.id}_themes{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'new themes_data={themes_data}')
                    logger.debug('save new themes_data')
                    object.themes = themes_data

            try:
                logger.debug('save updated Place object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the Place object: {e}')

            logger.info('return redirect place:list')
            return redirect('place:list')
        else:
            logger.error('form not is_valid')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')  
        form = PlaceForm(instance=object) # putback the form
        context = {'object': object, 'form': form}

    logger.info('return render place/update.html')
    return render(request, 'place/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Place delete_view')
    
    logger.debug('get Place object(pk)')
    object = get_object_or_404(Place, pk=pk)

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
                    logger.error(f'couldnt delete old images_data={old_image_path}: {e}')
            else:
                logger.debug('old images_data file not exists')

        # **古いファイルを削除**
        if object.themes:
            logger.debug('old themes_data exists')
            old_image_path = object.themes.path  # 旧ファイルのパス
            logger.debug(f'old themes_data={old_image_path}')
            if default_storage.exists(old_image_path):
                logger.debug('old themes_data file exists')
                try:
                    logger.debug('delete old themes_data')
                    default_storage.delete(old_image_path)  # 削除
                except Exception as e:
                    logger.error(f'couldnt delete old themes_data={old_image_path}: {e}')
            else:
                logger.debug('old themes_data file not exists')

        try:
            logger.debug('delete old Place object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete Place object: {e}')

        logger.info('return redirect place:list')
        return redirect('place:list')
    else:
        logger.info('GET method')

    logger.info('return render place/delete.html')
    return render(request, 'place/delete.html', context)

@csrf_exempt  # 関数デコレータに変更
@login_required
def push_likes(request, pk):
    logger.info('start Place push_likes')

    if request.method == 'POST':
        logger.info('POST method')

        place = get_object_or_404(Place, id=pk)
        logger.debug(f'get Place object(pk)={place}')

        # いいね処理を実行
        place.push_likes(request)

        # Ajaxにいいね数を返す
        logger.info(f'return likes:({place.likes})')
        return JsonResponse({'likes': f'({place.likes})'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def checkin_view(request): 
    logger.info('start Place checkin_view')

    # profile_own = operator
    try:
        profile_own = get_object_or_404(Profile, user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # place_with = target checkin place
    try:
        place_with_id = int(request.GET.get("place_with_id", 1)) # get place_with_id from URL query
        place_with = get_object_or_404(Place, pk=place_with_id) # get target place instance
        logger.debug(f'place_with={place_with}')
    except Exception as e:
        logger.error(f'couldnt get target place_with id={place_with_id}: {e}')
        place_with = None

    # checkin_record = latest CheckinRecord
    try:
        checkin_record = CheckinRecord.objects.filter(place=place_with, profile=profile_own).latest('pk')
        logger.debug(f'checkin_record={checkin_record}')
    except Exception as e:
        # 初回チェックイン時
        logger.info(f'couldnt get target checkin_record place={place_with} profile={profile_own}: {e}')
        checkin_record = None
    
    context = {'profile_own': profile_own, 'place_with': place_with, 'checkin_record': checkin_record}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報からProfile＆Place＆CheckinRecordを取得(POSTされたもののみ採用)
        profile_own_id_data = request.POST["profile_own_id"]
        profile_own = get_object_or_404(Profile, pk=profile_own_id_data)

        place_with_id_data = request.POST["place_with_id"]
        place_with = get_object_or_404(Place, pk=place_with_id_data)

        # GPS座標を取得して保存
        latitude_data = float(request.POST.get('latitude'))
        longitude_data = float(request.POST.get('longitude'))

        logger.debug(f'place_with.latitude={place_with.latitude}')
        logger.debug(f'latitude_data={latitude_data}')
        logger.debug(f'place_with.longitude={place_with.longitude}')
        logger.debug(f'longitude_data={longitude_data}')

        if not haversine(latitude_data, longitude_data, place_with.latitude, place_with.longitude):

            # チェックインする場所と操作者がGPS情報上近くにいない場合
            context.update({'errors': f'Not around by GPS Geolocation. Should more close to target'})

            logger.info('return render place/checkin.html')
            return render(request, 'place/checkin.html', context)
            
        # 初回ログイン時の処理
        if not checkin_record:
            logger.info('First checkin: No previous record found.')

            try:
                # 初回チェックインを作成
                checkin_record = CheckinRecord.objects.create(
                    place=place_with,
                    profile=profile_own,
                    checkin_time=now()
                )
                context.update({'messages': f'Successfully Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})
                context.update({'checkin_record': checkin_record})

            except Exception as e:
                logger.error(f'Failed to create CheckinRecord: {e}')
                context.update({'errors': 'Failed to create CheckinRecord.'})

        else:
            # 既にチェックイン済みでチェックアウトされていない場合はエラー
            if checkin_record.checkin_time and not checkin_record.checkout_time:
                logger.warning(f'Already checked in. Last Checked-In: {checkin_record.checkin_time}')
                context.update({'errors': f'Already Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})
            
            # チェックアウト済みなら新規チェックイン作成
            else:
                try:
                    new_checkin = CheckinRecord.objects.create(
                        place=place_with,
                        profile=profile_own,
                        checkin_time=now()
                    )
                    context.update({'messages': f'Successfully Checked-In at {new_checkin.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})
                    context.update({'checkin_record': new_checkin})

                except Exception as e:
                    logger.error(f'Failed to create new CheckinRecord: {e}')
                    context.update({'errors': 'Failed to create new CheckinRecord.'})
        
    else:
        logger.info('GET method')

        # チェックイン済みでチェックアウトがまだの場合はエラーメッセージを表示
        if checkin_record and checkin_record.checkin_time and not checkin_record.checkout_time:
            context.update({'errors': f'Already Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})


    logger.info('return render place/checkin.html')
    return render(request, 'place/checkin.html', context)


@login_required
def checkout_view(request): 
    logger.info('start Place checkout_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # place_with = target checkin place
    place_with_id = int(request.GET.get("place_with_id", 1)) # get place_with_id from URL query
    place_with = get_object_or_404(Place, pk=place_with_id) # get target place instance
    logger.debug(f'place_with={place_with}')

    # checkin_record = latest CheckinRecord
    checkin_record = CheckinRecord.objects.filter(place=place_with, profile=profile_own).latest('pk')
    logger.debug(f'checkin_record={checkin_record}')

    context = {'profile_own': profile_own, 'place_with': place_with, 'checkin_record': checkin_record}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報からProfile＆Placeを取得(POSTされたもののみ採用)
        profile_own_id_data = request.POST["profile_own_id"]
        profile_own = get_object_or_404(Profile, pk=profile_own_id_data)

        place_with_id_data = request.POST["place_with_id"]
        place_with = get_object_or_404(Place, pk=place_with_id_data)

        checkin_record_id_data = request.POST["checkin_record_id"]
        checkin_record = CheckinRecord.objects.get(pk=checkin_record_id_data)

        if checkin_record:
            # チェックアウト処理
            # place&profileが一致していて、チェックアウト時間が入っていないもののみ
            if checkin_record.profile == profile_own and checkin_record.place == place_with and not checkin_record.checkout_time:
                try:
                    checkin_record.checkout_time = now()
                    checkin_record.save()
                    context.update({'messages': f'Successfully Checked-Out at {checkin_record.checkout_time.strftime("%Y/%m/%d %H:%M:%S")}.'})
                except Exception as e:
                    checkin_record = CheckinRecord()
                    logger.error(f'couldnt update the Place CheckinRecord Object: {e}')
                    context.update({'errors': f'Couldnt Checked-Out.'})
            else:
                logger.error(f'couldnt update the Place CheckinRecord Object')
                context.update({'errors': f'Already Checked-Out at {checkin_record.checkout_time.strftime("%Y/%m/%d %H:%M:%S")}.'})
        else:
            context.update({'errors': 'No check-in record found. Please check-in first.'})

    else:
        logger.info('GET method')

        # 既にチェックアウト時間が設定されている場合はエラーメッセージを表示
        if checkin_record and checkin_record.checkout_time:
                context.update({'errors': f'Already Checked-Out at {checkin_record.checkout_time.strftime("%Y/%m/%d %H:%M:%S")}.'})
        elif checkin_record:
                context.update({'infos': f'Check-Out for Last Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}.'} )
        else:
            context.update({'errors': 'No previous check-in records found. Please check-in first.'})

    logger.info('return render place/checkout.html')
    return render(request, 'place/checkout.html', context)
