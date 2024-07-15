from django.db.models import Q, Case, When, IntegerField
from django.conf import settings
import random
from rest_framework import status as drf_status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from utils.imgproxy import ImgProxyOptions
from utils.response import APIResponse
from utils.pagination import APIPageNumberPagination
from article import models as article_models
from article import serializers as article_serializers


def get_paginated_data(queryset, request, serializer_class, data_key='new_data', *args, **kwargs):
    """
    快速分页
    """

    paginator = APIPageNumberPagination()
    data_page = paginator.paginate_queryset(queryset, request)

    if data_page is None:
        return APIResponse(status=drf_status.HTTP_400_BAD_REQUEST)
    serializer_class.context = kwargs.get('context', {})
    serialized_data = serializer_class(data_page, many=True).data
    return paginator.get_paginated_response(data={data_key: serialized_data})


def get_specify_sequence(uid_list_str, serializer_class, *args, **kwargs):
    """
    获取指定序列
    """

    uid_list = article_models.CategoryGroupRank.objects.filter(slug=uid_list_str)
    if not uid_list.exists():
        return []
    uid_list = uid_list.first().rank
    if not uid_list:
        return []

    article_list = article_models.Article.objects.filter(uid__in=uid_list).order_by(
        Case(*[When(uid=uid, then=index) for index, uid in enumerate(uid_list)]))
    serializer_class.context = kwargs.get('context', {})
    article_list_data = serializer_class(article_list, many=True).data

    return article_list_data


class IndexPageView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:index'

    @cache_response(timeout=settings.CACHE_TIME_INDEX, key_func='cache_key')
    def get(self, request):
        index_article_list = article_models.Article.objects.all().order_by('?')[:26]
        index_article_list_data = article_serializers.IndexArticleSerializer(index_article_list, many=True).data

        swiper_article_list = index_article_list_data[:4]

        trending_article_list = index_article_list_data[4:10]

        latest_article_list = index_article_list_data[10:14]
        editors_article_list = index_article_list_data[14:26]

        data = {
            'swiper_article_list': swiper_article_list,
            'trending_article_list': trending_article_list,

            'latest_article_list': latest_article_list,
            'editors_article_list': editors_article_list
        }

        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class ArticlePageView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:{kwargs.get("uid")}'

    @cache_response(timeout=settings.CACHE_TIME_DEATAIL, key_func='calculate_cache_key')
    def get(self, request, uid):
        article_obj = article_models.Article.objects.filter(uid=uid).first()
        if not article_obj:
            return APIResponse(status=drf_status.HTTP_404_NOT_FOUND)

        current_article_data = article_serializers.ArticleDetailSerializer(article_obj).data

        popular_article_list = article_models.Article.objects.exclude(uid=uid).order_by('?')[:10]
        popular_article_list_data = article_serializers.ArticleSimpleSerializer(popular_article_list, many=True,
                                                                                context={
                                                                                    'options': ImgProxyOptions.S_COVER_IMG}).data

        data = {
            'current_article': current_article_data,
            'popular_article_list': popular_article_list_data
        }
        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class QPageView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        q = request.query_params.get('q', None)
        sai_id = request.query_params.get('saiId', None)
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size')
        return f'backend:article:search:{q}:{page}:{size}:{sai_id}'

    @cache_response(timeout=settings.CACHE_TIME_Q, key_func='calculate_cache_key')
    def get(self, request):
        q = request.query_params.get('q', '')

        exact_articles = article_models.Article.objects.order_by(Case(
            When(title__icontains=q, then=0),
            When(description__icontains=q, then=1),
            default=2,
            output_field=IntegerField(),
        ))

        res = get_paginated_data(exact_articles, request, article_serializers.ArticleMiddleSerializer,
                                 'search_article_list', context={
                'options': ImgProxyOptions.S_COVER_IMG})

        sai_id = request.query_params.get('sai_id', None)
        search_ad_info = article_models.SearchAdInfo.objects.filter(uid=sai_id)

        if search_ad_info.exists():
            terms = [term.lower().strip() for term in search_ad_info.first().terms.split(',')]
            is_own = q.lower().strip() in terms
        else:
            is_own = False

        tagList = [
            ['Donate', 'Charity', 'Non-Profit', 'Tax Deduction', 'Car Donation', 'Motorcycle', 'Boat', 'Recycle'],
            ['Blueprint', 'Design', 'Model', 'Schema', 'Prototype', 'Concept', 'Production', 'Innovation'],
            ['Car', 'Truck', 'Bike', 'Bus', 'SUV', 'Van', 'Motorcycle', 'Automobile'],
            ['Fix', 'Restore', 'Maintenance', 'Service', 'Mechanics', 'Parts', 'Replace', 'Overhaul']
        ]
        tag = [random.sample(tags, min(6, len(tags))) for tags in tagList]

        res.data['data']['is_own'] = is_own
        res.data['data']['tagList'] = tag

        return res


class QDataView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        q = request.query_params.get('q', None)
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size')
        return f'backend:article:search:{q}:{page}:{size}'

    @cache_response(timeout=settings.CACHE_TIME_Q, key_func='calculate_cache_key')
    def get(self, request):
        q = request.query_params.get('q','')

        exact_articles = article_models.Article.objects.order_by(Case(
            When(title__icontains=q, then=0),
            When(description__icontains=q, then=1),
            default=2,
            output_field=IntegerField(),
        ))

        res = get_paginated_data(exact_articles, request, article_serializers.ArticleMiddleSerializer,
                                 'search_article_list', context={
                'options': ImgProxyOptions.S_COVER_IMG})

        return res


class ContentPageView(APIView):

    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:content:{kwargs.get("uid")}:{kwargs.get("slug")}'

    @cache_response(timeout=settings.CACHE_TIME_SEARCH_AD, key_func='calculate_cache_key')
    def get(self, request, uid, slug):
        try:
            search_ad_info = article_models.SearchAdInfo.objects.get(uid=uid)
            search_article = article_models.Article.objects.get(slug=slug)
        except Exception as e:
            return APIResponse(status=drf_status.HTTP_404_NOT_FOUND)

        search_ad_info_data = article_serializers.SearchAdInfoSerializer(search_ad_info).data
        search_article_data = article_serializers.SearchArticleSerializer(search_article).data
        data = {
            'search_ad_info': search_ad_info_data,
            'search_article': search_article_data
        }
        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class DiscussionPageView(APIView):

    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:discussion:{kwargs.get("uid")}:{kwargs.get("slug")}'

    @cache_response(timeout=settings.CACHE_TIME_SEARCH_AD, key_func='calculate_cache_key')
    def get(self, request, uid, slug):
        try:
            search_ad_info = article_models.SearchAdInfo.objects.get(uid=uid)
            search_article = article_models.Article.objects.get(slug=slug)
        except Exception as e:
            return APIResponse(status=drf_status.HTTP_404_NOT_FOUND)

        ad_article_map = {'KOTjSsb5': 'junk-cars-a-journey-of-value-and-opportunity',
                          '8D3UYUH6': 'roll-with-confidence-a-journey-through-tire-services',
                          'SAobOEx9': 'a-comprehensive-guide-to-donating-cars-for-kids',
                          'DbAnebTS': 'shield-and-shade-unveiling-the-magic-of-window-tinting',
                          'EgAJKXiu': 'experience-premium-pay-less-navigate-the-economical-oil-change-services',
                          '16rqaqX9': 'in-line-the-relevance-of-expert-car-alignment-services-nearby',
                          'iP5DtYjZ': 'glass-repairs-safeguarding-your-rides-panoramic-perspective',
                          '7LvDpCCc': 'fueling-financial-success-the-rise-of-online-vehicle-marketplaces',
                          'packGtF0': 'roadways-to-revenue-harnessing-the-power-of-online-vehicle-sale',
                          'sh8Q0kpB': 'unlocking-the-value-of-selling-your-car-online',
                          'hipmvlj3': 'empower-your-journey-discover-the-world-of-tire-services',
                          'OMtySHpI': 'discover-the-excitement-in-driving-with-the-2024-mazda-cx-50',
                          'Dd4qpaXC': 'rolling-into-the-future-the-electric-scooter-revolution',
                          '2b1iKILs': 'cash-on-wheels-steering-towards-a-sustainable-future-with-car-trade-ins',
                          'f2YdY2FU': 'driving-clean-the-journey-of-auto-detailing-excellence',
                          'EFdffjl2': 'steering-to-the-future-decoding-the-power-of-local-vehicle-repair-services',
                          'Njq4PZpm': 'navigating-the-wheels-a-guide-to-frugal-automotive-choices-in-2024',
                          'aiZ4YiZc': 'transforming-old-iron-into-gold',
                          'acNUsyby': 'revving-up-profits-unravel-the-world-of-cash-for-car-transactions',
                          'Pg0AjMCV': 'discover-your-dream-drive-luxury-innovation-and-convenience-at-your-fingertips',
                          'JieOpmrR': 'journey-with-trusted-allies-your-local-automotive-caregivers',
                          'jt8ymClB': 'a-sound-brake-check-can-break-your-worries',
                          '3Z52KUhp': 'ignite-change-with-your-car-donation',
                          '8LygZmFD': 'the-lifeblood-of-your-ride-exploring-the-importance-of-oil-changes',
                          'S2j2RWzA': 'unearth-the-unexpected-from-the-unwanted-the-art-of-selling-non-functioning-automobiles',
                          'WtqWLWuU': 'veterans-car-charity-compare-car-donation-charities',
                          'Xa3iXR39': 'decoding-the-basics-of-car-warranty-understanding-coverage-and-benefits',
                          'Bxo3Z9cM': 'a-closer-look-at-extended-car-warranties-drive-with-confidence',
                          'E21zPbvX': 'hit-the-jackpot-turn-your-vehicle-into-valuable-profit',
                          '5oG6Jg0e': 'how-donating-your-car-can-support-veteransdonations',
                          'GQdCufwO': 'virtual-vision-embrace-the-future-of-business-operations',
                          'ztgD5OJO': 'wired-in-unveiling-the-power-of-local-electrician-servicesservices',
                          'D8KuUEsN': 'transparency-unveiled-a-journey-through-the-looking-glass',
                          'QBlb7h7x': 'revitalize-your-abode-the-wonders-of-replacement-services',
                          'e5TLth3J': 'home-services-on-demand-finding-quality-near-you',
                          'pcMCXNAc': 'warmth-in-every-sip-celebrating-the-bliss-of-custom-and-personalized-mugs',
                          'gfpacZYY': 'the-power-of-posture-enhancing-workspaces-with-innovative-desks',
                          'WlejltNA': 'restoring-harmony-the-art-and-efficiency-of-home-and-auto-maintenance',
                          '3fJLvurF': 'guarding-the-canopy-the-case-for-leaf-guard-gutters',
                          'iu2dJxTJ': 'the-modern-gold-rush-understanding-ways-to-earn-money-in-todays-digital-era',
                          'Jf7d4QBz': 'navigating-comfort-an-insight-into-the-world-of-hvac-services',
                          'Y2fqF672': 'gateway-to-robustness-unraveling-the-criticality-of-garage-door-repairs-and-services',
                          'Z3xXK8Jq': 'unseen-heroes-exploring-the-world-of-septic-services',
                          'ZLA7uNHr': 'the-golden-trail-unraveling-the-path-to-precious-investments',
                          '9bMA1960': 'matrix-of-mobility-unraveling-the-world-of-qr-code-generation',
                          'aw7FHD8t': 'fulfilling-daily-duties-essential-services-for-your-perfect-home',
                          'RY8Hp3se': 'unraveling-comfort-the-art-and-utility-of-rugs-in-your-living-spaces',
                          'KQNO7QBU': 'the-essentials-of-modern-living-unveiling-best-in-class-products-and-services',
                          'wWwg9mjd': 'machines-of-marvel-enhancing-everyday-experience',
                          'cDBI60uC': 'footprints-of-excellence-the-art-and-craft-of-modern-flooring-solutions',
                          'VcLNxuiB': 'unlocking-secrets-of-security-a-closer-look-at-locksmith-services',
                          'j1P64Km8': 'the-assurance-of-reliable-plumbing-services-round-the-clock',
                          'JQbIKl3L': 'in-hot-water-demystifying-the-world-of-water-heater-services',
                          '8dXJ8Q6F': 'fluid-dynamics-at-work-proficient-plumbers-safeguarding-your-domestic-bliss',
                          'd4hMItMq': 'unlock-home-comforts-expert-maintenance-repair-and-installation-just-a-call-away',
                          's1HLw8QN': 'tailoring-creativity-the-art-of-customized-essentials',
                          '10MhPaHr': 'impressions-in-a-glance-the-power-of-logos-in-building-brands',
                          'wj1a2wye': 'fanning-the-flames-a-comprehensive-guide-to-furnace-maintenance-and-repair',
                          'mG57PQa3': 'unleashing-digital-power-the-transformative-journey-in-digital-marketing',
                          '5GTZXpfS': 'swiping-success-amplifying-business-with-seamless-credit-card-processing',
                          'eBOGAMXG': 'impressions-beyond-pixels-understanding-the-power-of-professional-printing-services',
                          'FwmKNYDc': 'essential-comforts-the-foundation-of-home-repair-services',
                          'FNQFRI6t': 'under-the-shield-celebrating-the-craft-of-roofing-professionals',
                          'SVsnKfXX': 'streamlining-success-one-payroll-at-a-time',
                          '8PpxLuhc': 'illuminating-the-payroll-pathway-for-success',
                          '4YppiSDq': 'empower-your-abode-office-with-security-and-efficacy',
                          'a8KHrW6d': 'under-the-shelter-of-security-exploring-the-world-of-roofing-services',
                          'uMQJU39V': 'shielding-your-sanctuary-a-dive-into-the-realm-of-home-security-solutions',
                          'xMq8c9DL': 'home-sweet-home-unleashing-the-power-of-local-services-for-a-comfortable-lifestyle',
                          'yS1noXQR': 'embracing-ease-exploring-the-benefits-of-walk-in-tubs-and-showers',
                          'BSWS39cL': 'embrace-the-future-navigating-the-digital-landscape',
                          'lKZTpnnA': 'diving-into-the-digital-unboxing-the-power-of-online-advertising',
                          'bRNLaNab': 'crowning-glory-exploring-the-multifaceted-world-of-roofing-services',
                          '3vygSwG6': 'cozy-comfort-under-your-feet-the-intricacies-of-the-carpet-industry',
                          'LAqZWVAH': 'chronicles-of-time-unfolding-stories-with-calendars',
                          '9XKcvI4r': 'checks-and-balances-navigating-the-world-of-modern-verification',
                          'KLzbBLcJ': 'ceramic-chronicles-a-journey-through-the-world-of-tiles',
                          '0C0d61kx': 'a-portal-to-panorama-elevating-your-space-with-window-and-door-solutions',
                          'VcUXPpQ7': 'ignite-change-with-your-car-donation-2',
                          'JAVXWD9B': 'american-homeowners-the-secrets-to-cost-effective-roofing',
                          'lQRVWrgb': 'killer-new-palisade-suv-attracts-every-customer',
                          'gov0QIh0': 'ultimate-comfort-suvs-for-elderly-indulge-in-the-comforts-of-a-luxury-suv',
                          'MQidl2oc': 'understanding-car-insurance',
                          'z6TH0ClG': 'hybrid-suv-an-eco-friendly-and-efficient-choice',
                          'oDzp7nne': 'economical-choices-for-seniors-buying-a-toyota-highlander',
                          '8RP8PZN0': 'senior-friendly-strategies-to-secure-a-budget-friendly-kona',
                          'O2SIrRBO': 'seniors-guide-to-buying-a-hyundai-ioniq-ev-on-a-budget',
                          'wpiTIfED': 'unsold-suvs-with-zero-miles-could-be-cheap-for-seniors',
                          'ZJNKvuQa': 'a-guide-for-seniors-on-purchasing-a-reasonably-priced-ram-1500',
                          'AuQ6ndTu': 'the-seniors-guide-to-buying-a-buick-on-a-budget',
                          'FVQYuboh': 'les-voitures-invendues-sont-vendues-pour-presque-rien',
                          'cDHyeUH8': 'killer-new-palisade-suv-attracts-every-customer',
                          'mFnJqI4F': 'a-guide-for-seniors-on-purchasing-a-reasonably-priced-ram-1500-2',
                          '8y4pk3KT': 'used-suvs-cars-2023-sales-affordable-prices-cant-be-missed',
                          'TLIwQXdp': 'new-small-hyundai-kona-for-seniors-the-price-might-surprise-you',
                          'N5xzx7xx': 'how-seniors-can-get-toyota-rav4s-on-a-budget-practical-buying-tips',
                          'oSbxqYq7': 'unsold-cars-for-seniors-are-almost-being-given-away',
                          'uh8lrqvx': 'best-suv-buy-deals-new-leftover-suvs-are-nearly-being-given-away',
                          'wPThKqEo': 'discover-the-new-volvo-in-2025-setting-trends-for-the-future',
                          'cTVNqAcP': 'exploring-the-unmatched-appeal-of-the-new-jeep-grand-cherokee',
                          'is8Dp4f6': 'oil-change-coupons-for-seniors',
                          'LT4WPS9o': 'oil-change-coupons-your-ultimate-guide',
                          'vwi1SJ8S': 'killer-new-palisade-suv-attracts-every-customer-2',
                          'djuMhcPB': 'killer-new-hyundai-santafe-2024-in-hong-kong',
                          'Ooun0A2z': 'les-voitures-invendues-sont-vendues-pour-presque-rien-2',
                          'QNIxsYn9': 'understanding-car-insurance-2',
                          'S7ocqhtJ': 'the-killer-new-mazda-cx-30-is-close-to-perfection',
                          'JEdB7GA1': 'new-ram-1500-clearance-sale-prices-might-surprise-you',
                          'MQHBzlNV': 'how-to-buy-a-reliable-used-car-on-a-budget',
                          'NoTwxhJR': 'killer-new-palisade-suv-attracts-every-custome',
                          'b0TvVR9E': 'unsold-cars-for-seniors-are-almost-being-given-away-2'}
        try:
            del ad_article_map[uid]
        except Exception as e:
            pass

        random_keys = random.sample(list(ad_article_map), 5)
        # 使用这些键来获取对应的值，得到随机的键值对
        random_values = [ad_article_map[key] for key in random_keys]

        search_ad_info_data = article_serializers.SearchAdInfoSerializer(search_ad_info).data
        search_article_data = article_serializers.SearchArticleSerializer(search_article).data

        share_first_article_list = article_models.Article.objects.filter(slug=slug)

        articles = article_models.Article.objects.filter(slug__in=random_values).order_by(
            Case(*[When(slug=slug, then=index) for index, slug in enumerate(random_values)])
        )
        # 将 random_slug_list 和 articles 配对，并将每个配对的元素组合成一个字典
        share_other_article_list = list(
            {"uid": uid, "article": article} for uid, article in zip(random_keys, articles))
        article_list = [{"uid": uid, "article": article} for article in share_first_article_list]
        share_article_list = article_list + share_other_article_list

        share_article_data = article_serializers.DiscussionSerializer(share_article_list, many=True).data

        data = {
            'search_ad_info': search_ad_info_data,
            'search_article': search_article_data,
            'share_article_list': share_article_data
        }
        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class CategoryPageView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:category:{kwargs.get("slug")}'

    @cache_response(timeout=settings.CACHE_TIME_CATEGORY, key_func='calculate_cache_key')
    def get(self, request, slug):
        # 当前分类
        current_category = article_models.Category.objects.filter(slug=slug).first()
        if not current_category:
            return APIResponse(status=drf_status.HTTP_404_NOT_FOUND)

        category_article_list = get_specify_sequence(slug, article_serializers.CategoryArticleSerializer)

        top_article_data = category_article_list[0]

        trending_article_list_data = category_article_list[1:]

        uid_list = article_models.CategoryGroupRank.objects.filter(slug=slug).first()

        if not uid_list:
            uid_list = []
        else:
            uid_list = uid_list.rank

        recent_article_list = article_models.Article.objects.exclude(
            uid__in=uid_list).filter(categories__slug=slug).order_by('-update_time')
        res = get_paginated_data(recent_article_list, request, article_serializers.CategoryArticleSerializer,
                                 'recent_article_list')

        res.data['data']['top_article'] = top_article_data
        res.data['data']['trending_article_list'] = trending_article_list_data

        return res


class CategoryDataView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        slug = kwargs.get('slug')
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size')
        return f'backend:article:API:category:{slug}:{page}:{size}'

    @cache_response(timeout=settings.CACHE_TIME_API_DATA, key_func='cache_key')
    def get(self, request, slug):

        uid_list = article_models.CategoryGroupRank.objects.filter(slug=slug).first()

        if not uid_list:
            uid_list = []
        else:
            uid_list = uid_list.rank

        recent_article_list = article_models.Article.objects.exclude(
            uid__in=uid_list).filter(categories__slug=slug).order_by('-update_time')
        res = get_paginated_data(recent_article_list, request, article_serializers.CategoryArticleSerializer,
                                 'recent_article_list')
        return res
