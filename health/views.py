import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import (
    HealthSettings, HealthCondition, Food, Fruit, Vegetable,
    Herb, Recipe, Video, Favorite, FoodDiary, FoodDiaryEntry,
    MealPlan, MealPlanItem, HealthJournal,
    FoodCategory, FoodItem, FoodItemGrowingImage,
    FoodItemRecipeVideo, FoodItemGrowingVideo,
)


def super_admin_required(view_func):
    from functools import wraps
    from django.contrib.auth import get_user_model
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.admin_role != 'super_admin':
            messages.error(request, 'Super Admin access required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── HOME ──────────────────────────────────────────────────────────────────────

def health_home(request):
    return redirect('/health/guide/')


# ── CONDITIONS ────────────────────────────────────────────────────────────────

def condition_detail(request, slug):
    condition = get_object_or_404(HealthCondition, slug=slug)
    foods     = condition.foods.all()[:8]
    fruits    = condition.fruits.all()[:8]
    vegetables = condition.vegetables.all()[:8]
    herbs     = condition.herbs.all()[:6]
    recipes   = condition.recipes.all()[:6]
    videos    = condition.videos.all()[:4]
    faq = []
    if condition.faq:
        try:
            faq = json.loads(condition.faq)
        except Exception:
            pass
    return render(request, 'health/condition_detail.html', {
        'condition': condition,
        'foods': foods, 'fruits': fruits,
        'vegetables': vegetables, 'herbs': herbs,
        'recipes': recipes, 'videos': videos,
        'faq': faq,
    })


# ── FOOD ──────────────────────────────────────────────────────────────────────

def food_list(request):
    q   = request.GET.get('q', '')
    qs  = Food.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/food_list.html', {'foods': qs, 'q': q})


def food_detail(request, slug):
    food    = get_object_or_404(Food, slug=slug)
    related = Food.objects.exclude(pk=food.pk)[:4]
    is_fav  = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='food', item_id=food.pk).exists()
    return render(request, 'health/food_detail.html', {'food': food, 'related': related, 'is_fav': is_fav})


# ── FRUITS ────────────────────────────────────────────────────────────────────

def fruit_list(request):
    q  = request.GET.get('q', '')
    qs = Fruit.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/fruit_list.html', {'fruits': qs, 'q': q})


def fruit_detail(request, slug):
    fruit   = get_object_or_404(Fruit, slug=slug)
    is_fav  = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='fruit', item_id=fruit.pk).exists()
    return render(request, 'health/fruit_detail.html', {'fruit': fruit, 'is_fav': is_fav})


# ── VEGETABLES ────────────────────────────────────────────────────────────────

def vegetable_list(request):
    q  = request.GET.get('q', '')
    qs = Vegetable.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/vegetable_list.html', {'vegetables': qs, 'q': q})


def vegetable_detail(request, slug):
    veg    = get_object_or_404(Vegetable, slug=slug)
    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='vegetable', item_id=veg.pk).exists()
    return render(request, 'health/vegetable_detail.html', {'veg': veg, 'is_fav': is_fav})


# ── HERBS ─────────────────────────────────────────────────────────────────────

def herb_list(request):
    q  = request.GET.get('q', '')
    qs = Herb.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/herb_list.html', {'herbs': qs, 'q': q})


def herb_detail(request, slug):
    herb   = get_object_or_404(Herb, slug=slug)
    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='herb', item_id=herb.pk).exists()
    return render(request, 'health/herb_detail.html', {'herb': herb, 'is_fav': is_fav})


# ── RECIPES ───────────────────────────────────────────────────────────────────

def recipe_list(request):
    q        = request.GET.get('q', '')
    category = request.GET.get('cat', '')
    qs       = Recipe.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category=category)
    return render(request, 'health/recipe_list.html', {
        'recipes': qs, 'q': q, 'category': category,
        'categories': Recipe.CATEGORY,
    })


def recipe_detail(request, slug):
    recipe  = get_object_or_404(Recipe, slug=slug)
    is_fav  = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='recipe', item_id=recipe.pk).exists()
    ingredients = [i.strip() for i in recipe.ingredients.splitlines() if i.strip()]
    steps       = [s.strip() for s in recipe.steps.splitlines() if s.strip()]
    return render(request, 'health/recipe_detail.html', {
        'recipe': recipe, 'is_fav': is_fav,
        'ingredients': ingredients, 'steps': steps,
    })


# ── VIDEOS ────────────────────────────────────────────────────────────────────

def video_list(request):
    category = request.GET.get('cat', '')
    qs       = Video.objects.all()
    if category:
        qs = qs.filter(category=category)
    return render(request, 'health/video_list.html', {
        'videos': qs, 'category': category,
        'categories': Video.CATEGORY,
    })


# ── AI CHAT ───────────────────────────────────────────────────────────────────

def health_chat(request):
    return render(request, 'health/chat.html')


@login_required
def health_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Rate limit: 20 requests per user per hour
    from django.core.cache import cache
    cache_key = f'health_chat_{request.user.pk}'
    count = cache.get(cache_key, 0)
    if count >= 20:
        return JsonResponse({'error': 'Too many requests. Please try again later.'}, status=429)
    cache.set(cache_key, count + 1, 3600)
    try:
        body    = json.loads(request.body)
        message = body.get('message', '').strip()
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    from django.conf import settings as django_settings
    hs      = HealthSettings.get()
    api_key = hs.groq_api_key or getattr(django_settings, 'GROQ_API_KEY', '')

    if not api_key:
        return JsonResponse({'reply': (
            "AI assistant is not configured yet. "
            "Please ask the admin to add the Groq API key in Health Settings.\n\n"
            "⚠️ This is educational information only, not medical advice."
        )})

    try:
        from groq import Groq
        client   = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[
                {'role': 'system', 'content': hs.ai_system_prompt},
                {'role': 'user',   'content': message},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except ImportError:
        reply = ("AI library not installed on server. "
                 "Run: pip install groq\n\n"
                 "⚠️ This is educational information only, not medical advice.")
    except Exception as e:
        reply = ("AI is temporarily unavailable. Please try again later.\n\n"
                 "⚠️ This is educational information only, not medical advice.")

    return JsonResponse({'reply': reply})


# ── FAVORITES ─────────────────────────────────────────────────────────────────

@login_required
def health_favorites(request):
    favs = Favorite.objects.filter(user=request.user).order_by('-created_at')
    data = {'foods': [], 'fruits': [], 'vegetables': [], 'herbs': [], 'recipes': [], 'videos': []}
    for f in favs:
        try:
            if f.item_type == 'food':
                data['foods'].append(Food.objects.get(pk=f.item_id))
            elif f.item_type == 'fruit':
                data['fruits'].append(Fruit.objects.get(pk=f.item_id))
            elif f.item_type == 'vegetable':
                data['vegetables'].append(Vegetable.objects.get(pk=f.item_id))
            elif f.item_type == 'herb':
                data['herbs'].append(Herb.objects.get(pk=f.item_id))
            elif f.item_type == 'recipe':
                data['recipes'].append(Recipe.objects.get(pk=f.item_id))
            elif f.item_type == 'video':
                data['videos'].append(Video.objects.get(pk=f.item_id))
        except Exception:
            pass
    return render(request, 'health/favorites.html', {'data': data})


@login_required
def toggle_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body      = json.loads(request.body)
        item_type = body.get('type')
        item_id   = int(body.get('id'))
    except Exception:
        return JsonResponse({'error': 'Invalid'}, status=400)
    obj, created = Favorite.objects.get_or_create(
        user=request.user, item_type=item_type, item_id=item_id
    )
    if not created:
        obj.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})


# ── FOOD DIARY ────────────────────────────────────────────────────────────────

@login_required
def food_diary(request):
    from datetime import date
    today  = date.today()
    d_str  = request.GET.get('date', str(today))
    try:
        from datetime import datetime
        diary_date = datetime.strptime(d_str, '%Y-%m-%d').date()
    except Exception:
        diary_date = today
    diary, _  = FoodDiary.objects.get_or_create(user=request.user, date=diary_date)
    entries   = diary.entries.all()
    recent    = FoodDiary.objects.filter(user=request.user).exclude(date=diary_date)[:7]
    return render(request, 'health/diary.html', {
        'diary': diary, 'entries': entries,
        'diary_date': diary_date, 'today': today,
        'recent': recent,
        'meal_types': FoodDiaryEntry.MEAL,
    })


@login_required
def food_diary_save(request):
    if request.method != 'POST':
        return redirect('food_diary')
    from datetime import date, datetime
    diary_date = request.POST.get('date', str(date.today()))
    try:
        diary_date = datetime.strptime(diary_date, '%Y-%m-%d').date()
    except Exception:
        diary_date = date.today()

    diary, _ = FoodDiary.objects.get_or_create(user=request.user, date=diary_date)

    action = request.POST.get('action', '')
    if action == 'add_entry':
        meal_type = request.POST.get('meal_type', '')
        food_name = request.POST.get('food_name', '').strip()
        quantity  = request.POST.get('quantity', '').strip()
        calories  = request.POST.get('calories', '') or None
        if food_name:
            FoodDiaryEntry.objects.create(
                diary=diary, meal_type=meal_type,
                food_name=food_name, quantity=quantity,
                calories=int(calories) if calories else None,
            )
    elif action == 'delete_entry':
        entry_id = request.POST.get('entry_id')
        FoodDiaryEntry.objects.filter(pk=entry_id, diary__user=request.user).delete()
    elif action == 'update_water':
        diary.water_glasses = int(request.POST.get('water_glasses', 0))
        diary.save()
    elif action == 'update_notes':
        diary.notes = request.POST.get('notes', '')
        diary.save()

    return redirect(f'/health/diary/?date={diary_date}')


# ── MEAL PLANNER ──────────────────────────────────────────────────────────────

@login_required
def meal_planner(request):
    plans   = MealPlan.objects.filter(user=request.user)
    recipes = Recipe.objects.all()
    active  = plans.first()
    items   = {}
    if active:
        for item in active.items.select_related('recipe'):
            key = f"{item.date}_{item.meal_type}"
            items[key] = item
    return render(request, 'health/planner.html', {
        'plans': plans, 'active': active,
        'items': items, 'recipes': recipes,
        'meal_types': MealPlanItem.MEAL,
    })


@login_required
def meal_planner_save(request):
    if request.method != 'POST':
        return redirect('meal_planner')
    action = request.POST.get('action')
    if action == 'create_plan':
        from datetime import datetime
        name  = request.POST.get('name', 'My Meal Plan').strip()
        start = request.POST.get('start_date')
        end   = request.POST.get('end_date')
        try:
            start = datetime.strptime(start, '%Y-%m-%d').date()
            end   = datetime.strptime(end,   '%Y-%m-%d').date()
            MealPlan.objects.create(user=request.user, name=name, start_date=start, end_date=end)
            messages.success(request, f'Meal plan "{name}" created.')
        except Exception:
            messages.error(request, 'Invalid dates.')
    elif action == 'add_item':
        from datetime import datetime
        plan_id   = request.POST.get('plan_id')
        plan      = get_object_or_404(MealPlan, pk=plan_id, user=request.user)
        item_date = request.POST.get('item_date')
        meal_type = request.POST.get('meal_type')
        recipe_id = request.POST.get('recipe_id') or None
        custom    = request.POST.get('custom', '').strip()
        try:
            item_date = datetime.strptime(item_date, '%Y-%m-%d').date()
            recipe    = Recipe.objects.get(pk=recipe_id) if recipe_id else None
            MealPlanItem.objects.update_or_create(
                plan=plan, date=item_date, meal_type=meal_type,
                defaults={'recipe': recipe, 'custom': custom}
            )
        except Exception:
            messages.error(request, 'Could not save item.')
    elif action == 'delete_plan':
        plan_id = request.POST.get('plan_id')
        MealPlan.objects.filter(pk=plan_id, user=request.user).delete()
        messages.success(request, 'Plan deleted.')
    return redirect('meal_planner')


# ── SHOPPING LIST ─────────────────────────────────────────────────────────────

@login_required
def shopping_list(request):
    plan_id = request.GET.get('plan')
    plan    = None
    items   = []
    if plan_id:
        plan = get_object_or_404(MealPlan, pk=plan_id, user=request.user)
        seen = set()
        for mi in plan.items.select_related('recipe'):
            if mi.recipe:
                for line in mi.recipe.ingredients.splitlines():
                    line = line.strip()
                    if line and line not in seen:
                        items.append(line)
                        seen.add(line)
    plans = MealPlan.objects.filter(user=request.user)
    return render(request, 'health/shopping_list.html', {
        'plan': plan, 'items': items, 'plans': plans,
    })


# ── PROGRESS ──────────────────────────────────────────────────────────────────

@login_required
def health_progress(request):
    from datetime import date, timedelta
    today     = date.today()
    diary_count = FoodDiary.objects.filter(user=request.user).count()
    plan_count  = MealPlan.objects.filter(user=request.user).count()
    fav_count   = Favorite.objects.filter(user=request.user).count()
    streak = 0
    for i in range(30):
        d = today - timedelta(days=i)
        if FoodDiary.objects.filter(user=request.user, date=d).exists():
            streak += 1
        else:
            break
    return render(request, 'health/progress.html', {
        'diary_count': diary_count, 'plan_count': plan_count,
        'fav_count': fav_count, 'streak': streak,
    })


# ── SEARCH ────────────────────────────────────────────────────────────────────

def health_search(request):
    q   = request.GET.get('q', '').strip()
    results = {}
    if q:
        results['conditions']  = HealthCondition.objects.filter(name__icontains=q)
        results['foods']       = Food.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['fruits']      = Fruit.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['vegetables']  = Vegetable.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['herbs']       = Herb.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['recipes']     = Recipe.objects.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, 'health/search.html', {'q': q, 'results': results})


# ── ADMIN VIEWS ───────────────────────────────────────────────────────────────

@super_admin_required
def hadmin_dashboard(request):
    return render(request, 'health/admin/dashboard.html', {
        'cond_count':     HealthCondition.objects.count(),
        'food_count':     Food.objects.count(),
        'fruit_count':    Fruit.objects.count(),
        'veg_count':      Vegetable.objects.count(),
        'herb_count':     Herb.objects.count(),
        'recipe_count':   Recipe.objects.count(),
        'video_count':    Video.objects.count(),
        'journal_count':  HealthJournal.objects.count(),
        'guide_cat_count': FoodCategory.objects.count(),
        'guide_item_count': FoodItem.objects.count(),
        'user_count':     Favorite.objects.values('user').distinct().count(),
    })


def _hadmin_crud(request, Model, template, list_url, fields, slug_from='name'):
    if request.method == 'POST':
        pk     = request.POST.get('pk')
        action = request.POST.get('action', 'save')
        if action == 'delete' and pk:
            Model.objects.filter(pk=pk).delete()
            messages.success(request, 'Deleted.')
            return redirect(list_url)
        data = {f: request.POST.get(f, '') for f in fields if f not in ('image',)}
        for bool_field in ('is_featured', 'diabetes_safe'):
            if bool_field in fields:
                data[bool_field] = bool_field in request.POST
        if 'slug' in fields and not data.get('slug'):
            data['slug'] = slugify(data.get(slug_from, ''))
        if pk:
            obj = get_object_or_404(Model, pk=pk)
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
            messages.success(request, 'Updated.')
        else:
            obj = Model(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
            messages.success(request, 'Created.')
        return redirect(list_url)
    return None


@super_admin_required
def hadmin_conditions(request):
    return render(request, 'health/admin/condition_list.html',
                  {'items': HealthCondition.objects.all()})


@super_admin_required
def hadmin_condition_edit(request, pk=None):
    obj = get_object_or_404(HealthCondition, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','icon','overview','foods_to_eat','foods_to_limit',
                  'fruits_info','vegetables_info','herbs_info','spices_info',
                  'cooking_methods','meal_timing','portion_guidance','faq','order']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = HealthCondition(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_conditions')
    return render(request, 'health/admin/condition_edit.html', {'obj': obj})


@super_admin_required
def hadmin_condition_delete(request, pk):
    get_object_or_404(HealthCondition, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_conditions')


@super_admin_required
def hadmin_foods(request):
    return render(request, 'health/admin/food_list.html',
                  {'items': Food.objects.all()})


@super_admin_required
def hadmin_food_edit(request, pk=None):
    obj = get_object_or_404(Food, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','description','scientific_name','nutrition_facts',
                  'benefits','suitable_for','avoid_if','best_time','serving_size','cooking_methods']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Food(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_foods')
    return render(request, 'health/admin/food_edit.html', {'obj': obj})


@super_admin_required
def hadmin_food_delete(request, pk):
    get_object_or_404(Food, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_foods')


@super_admin_required
def hadmin_fruits(request):
    return render(request, 'health/admin/fruit_list.html',
                  {'items': Fruit.objects.all()})


@super_admin_required
def hadmin_fruit_edit(request, pk=None):
    obj = get_object_or_404(Fruit, pk=pk) if pk else None
    conditions = HealthCondition.objects.all()
    if request.method == 'POST':
        fields = ['name','slug','description','nutrition','benefits',
                  'serving_size','best_time','diabetes_note',
                  'natural_treatment','video_url']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured']   = 'is_featured' in request.POST
        data['diabetes_safe'] = 'diabetes_safe' in request.POST
        # Build condition_advice JSON from POST
        import json as _json
        advice = {}
        for c in conditions:
            can_eat = request.POST.get(f'ca_can_{c.slug}', '')
            note    = request.POST.get(f'ca_note_{c.slug}', '').strip()
            if can_eat or note:
                advice[c.slug] = {'can_eat': can_eat, 'note': note, 'name': c.name, 'icon': c.icon}
        data['condition_advice'] = _json.dumps(advice, ensure_ascii=False)
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Fruit(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_fruits')
    import json as _json
    advice = {}
    if obj and obj.condition_advice:
        try: advice = _json.loads(obj.condition_advice)
        except: advice = {}
    return render(request, 'health/admin/fruit_edit.html', {'obj': obj, 'conditions': conditions, 'advice': advice})


@super_admin_required
def hadmin_fruit_delete(request, pk):
    get_object_or_404(Fruit, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_fruits')


@super_admin_required
def hadmin_vegetables(request):
    return render(request, 'health/admin/vegetable_list.html',
                  {'items': Vegetable.objects.all()})


@super_admin_required
def hadmin_vegetable_edit(request, pk=None):
    obj = get_object_or_404(Vegetable, pk=pk) if pk else None
    conditions = HealthCondition.objects.all()
    if request.method == 'POST':
        fields = ['name','slug','description','nutrition','benefits',
                  'cooking_methods','best_time','serving_size',
                  'natural_treatment','video_url']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        import json as _json
        advice = {}
        for c in conditions:
            can_eat = request.POST.get(f'ca_can_{c.slug}', '')
            note    = request.POST.get(f'ca_note_{c.slug}', '').strip()
            if can_eat or note:
                advice[c.slug] = {'can_eat': can_eat, 'note': note, 'name': c.name, 'icon': c.icon}
        data['condition_advice'] = _json.dumps(advice, ensure_ascii=False)
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Vegetable(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_vegetables')
    import json as _json
    advice = {}
    if obj and obj.condition_advice:
        try: advice = _json.loads(obj.condition_advice)
        except: advice = {}
    return render(request, 'health/admin/vegetable_edit.html', {'obj': obj, 'conditions': conditions, 'advice': advice})


@super_admin_required
def hadmin_vegetable_delete(request, pk):
    get_object_or_404(Vegetable, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_vegetables')


@super_admin_required
def hadmin_herbs(request):
    return render(request, 'health/admin/herb_list.html',
                  {'items': Herb.objects.all()})


@super_admin_required
def hadmin_herb_edit(request, pk=None):
    obj = get_object_or_404(Herb, pk=pk) if pk else None
    conditions = HealthCondition.objects.all()
    if request.method == 'POST':
        fields = ['name','slug','description','traditional_uses',
                  'scientific_evidence','preparation','benefits','precautions',
                  'natural_treatment','video_url']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        import json as _json
        advice = {}
        for c in conditions:
            can_eat = request.POST.get(f'ca_can_{c.slug}', '')
            note    = request.POST.get(f'ca_note_{c.slug}', '').strip()
            if can_eat or note:
                advice[c.slug] = {'can_eat': can_eat, 'note': note, 'name': c.name, 'icon': c.icon}
        data['condition_advice'] = _json.dumps(advice, ensure_ascii=False)
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Herb(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_herbs')
    import json as _json
    advice = {}
    if obj and obj.condition_advice:
        try: advice = _json.loads(obj.condition_advice)
        except: advice = {}
    return render(request, 'health/admin/herb_edit.html', {'obj': obj, 'conditions': conditions, 'advice': advice})


@super_admin_required
def hadmin_herb_delete(request, pk):
    get_object_or_404(Herb, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_herbs')


@super_admin_required
def hadmin_recipes(request):
    return render(request, 'health/admin/recipe_list.html',
                  {'items': Recipe.objects.all()})


@super_admin_required
def hadmin_recipe_edit(request, pk=None):
    obj = get_object_or_404(Recipe, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','category','description','ingredients','steps',
                  'nutrition','difficulty','video_url']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        for int_field in ['calories','prep_time','cook_time','servings']:
            val = request.POST.get(int_field, '') or None
            data[int_field] = int(val) if val else None
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Recipe(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_recipes')
    return render(request, 'health/admin/recipe_edit.html', {
        'obj': obj, 'categories': Recipe.CATEGORY, 'difficulties': Recipe.DIFFICULTY,
    })


@super_admin_required
def hadmin_recipe_delete(request, pk):
    get_object_or_404(Recipe, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_recipes')


@super_admin_required
def hadmin_videos(request):
    return render(request, 'health/admin/video_list.html',
                  {'items': Video.objects.all()})


@super_admin_required
def hadmin_video_edit(request, pk=None):
    obj = get_object_or_404(Video, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['title','youtube_url','category','description']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.thumbnail = request.FILES['image']
            obj.save()
        else:
            obj = Video(**data)
            if 'image' in request.FILES:
                obj.thumbnail = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_videos')
    return render(request, 'health/admin/video_edit.html', {
        'obj': obj, 'categories': Video.CATEGORY,
    })


@super_admin_required
def hadmin_video_delete(request, pk):
    get_object_or_404(Video, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_videos')


@super_admin_required
def hadmin_settings(request):
    settings = HealthSettings.get()
    if request.method == 'POST':
        settings.gemini_api_key   = request.POST.get('gemini_api_key', '').strip()
        settings.groq_api_key     = request.POST.get('groq_api_key', '').strip()
        settings.ai_system_prompt = request.POST.get('ai_system_prompt', '').strip()
        settings.daily_tip        = request.POST.get('daily_tip', '').strip()
        settings.site_tagline     = request.POST.get('site_tagline', '').strip()
        settings.save()
        messages.success(request, 'Settings saved.')
        return redirect('hadmin_settings')
    return render(request, 'health/admin/settings.html', {'settings': settings})


# ── JOURNAL ADMIN ─────────────────────────────────────────────────────────────

@super_admin_required
def hadmin_journals(request):
    return render(request, 'health/admin/journal_list.html',
                  {'items': HealthJournal.objects.all()})


@super_admin_required
def hadmin_journal_edit(request, pk=None):
    obj = get_object_or_404(HealthJournal, pk=pk) if pk else None
    if request.method == 'POST':
        from django.utils import timezone
        fields = ['title', 'slug', 'category', 'summary', 'content', 'video_url']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_published'] = 'is_published' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['title'])
        if data['is_published'] and (not obj or not obj.published_at):
            data['published_at'] = timezone.now()
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = HealthJournal(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Journal saved.')
        return redirect('hadmin_journals')
    return render(request, 'health/admin/journal_edit.html', {
        'obj': obj, 'categories': HealthJournal.CATEGORY,
    })


@super_admin_required
def hadmin_journal_delete(request, pk):
    get_object_or_404(HealthJournal, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_journals')


# ── JOURNAL USER VIEWS ────────────────────────────────────────────────────────

def journal_list(request):
    category = request.GET.get('cat', '')
    qs = HealthJournal.objects.filter(is_published=True)
    if category:
        qs = qs.filter(category=category)
    return render(request, 'health/journal_list.html', {
        'journals': qs, 'categories': HealthJournal.CATEGORY, 'active_cat': category,
    })


def journal_detail(request, slug):
    journal = get_object_or_404(HealthJournal, slug=slug, is_published=True)
    related = HealthJournal.objects.filter(is_published=True, category=journal.category).exclude(pk=journal.pk)[:3]
    return render(request, 'health/journal_detail.html', {'journal': journal, 'related': related})


# ── FOOD GUIDE ADMIN ──────────────────────────────────────────────────────────

@super_admin_required
def hadmin_guide_categories(request):
    return render(request, 'health/admin/guide_category_list.html',
                  {'items': FoodCategory.objects.all()})


@super_admin_required
def hadmin_guide_category_edit(request, pk=None):
    obj = get_object_or_404(FoodCategory, pk=pk) if pk else None
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        slug_val    = request.POST.get('slug', '').strip() or slugify(name)
        icon        = request.POST.get('icon', '🥗').strip()
        description = request.POST.get('description', '').strip()
        order       = int(request.POST.get('order', 0) or 0)
        is_active   = 'is_active' in request.POST
        if obj:
            obj.name = name; obj.slug = slug_val; obj.icon = icon
            obj.description = description; obj.order = order; obj.is_active = is_active
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = FoodCategory(name=name, slug=slug_val, icon=icon,
                               description=description, order=order, is_active=is_active)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Category saved.')
        return redirect('hadmin_guide_categories')
    return render(request, 'health/admin/guide_category_edit.html', {'obj': obj})


@super_admin_required
def hadmin_guide_category_delete(request, pk):
    get_object_or_404(FoodCategory, pk=pk).delete()
    messages.success(request, 'Category deleted.')
    return redirect('hadmin_guide_categories')


@super_admin_required
def hadmin_guide_items(request):
    cat_id     = request.GET.get('cat', '')
    categories = FoodCategory.objects.all()
    qs         = FoodItem.objects.select_related('category').all()
    if cat_id:
        qs = qs.filter(category_id=cat_id)
    return render(request, 'health/admin/guide_item_list.html',
                  {'items': qs, 'categories': categories, 'active_cat': cat_id})


@super_admin_required
def hadmin_guide_item_edit(request, pk=None):
    obj            = get_object_or_404(FoodItem, pk=pk) if pk else None
    categories     = FoodCategory.objects.filter(is_active=True)
    conditions     = HealthCondition.objects.all()
    growing_images  = obj.growing_images.all() if obj else []
    recipe_videos   = obj.recipe_videos.all() if obj else []
    growing_videos  = obj.growing_videos.all() if obj else []

    if request.method == 'POST':
        cat_id   = request.POST.get('category_id')
        category = get_object_or_404(FoodCategory, pk=cat_id) if cat_id else None
        fields   = ['name', 'slug', 'description',
                    'advice_video_url', 'advice_youtube_channel',
                    'recipe_content', 'recipe_video_url', 'recipe_youtube_channel',
                    'growing_content', 'growing_video_url', 'growing_youtube_channel',
                    'journal_content', 'journal_video_url', 'journal_youtube_channel', 'journal_author',
                    'nutrition', 'benefits',
                    'natural_treatment', 'natural_treatment_video_url', 'natural_treatment_youtube_channel']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        data['order']       = int(request.POST.get('order', 0) or 0)
        data['category']    = category
        import json as _json
        advice = {}
        for c in conditions:
            can_eat = request.POST.get(f'ca_can_{c.slug}', '')
            note    = request.POST.get(f'ca_note_{c.slug}', '').strip()
            if can_eat or note:
                advice[c.slug] = {'can_eat': can_eat, 'note': note, 'name': c.name, 'icon': c.icon}
        data['condition_advice'] = _json.dumps(advice, ensure_ascii=False)
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            for vfield in ('advice_video', 'recipe_video', 'growing_video', 'journal_video', 'natural_treatment_video'):
                if vfield in request.FILES:
                    setattr(obj, vfield, request.FILES[vfield])
                elif request.POST.get(f'clear_{vfield}'):
                    setattr(obj, vfield, None)
            obj.save()
        else:
            obj = FoodItem(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            for vfield in ('advice_video', 'recipe_video', 'growing_video', 'journal_video', 'natural_treatment_video'):
                if vfield in request.FILES:
                    setattr(obj, vfield, request.FILES[vfield])
            obj.save()
        for img_file in request.FILES.getlist('growing_images'):
            FoodItemGrowingImage.objects.create(item=obj, image=img_file)
        del_ids = request.POST.getlist('delete_growing_image')
        if del_ids:
            FoodItemGrowingImage.objects.filter(pk__in=del_ids, item=obj).delete()

        # Save new recipe videos
        new_rv_titles    = request.POST.getlist('new_recipe_title')
        new_rv_channels  = request.POST.getlist('new_recipe_channel')
        new_rv_urls      = request.POST.getlist('new_recipe_url')
        new_rv_files     = request.FILES.getlist('new_recipe_file')
        for i, title in enumerate(new_rv_titles):
            url  = new_rv_urls[i]  if i < len(new_rv_urls)  else ''
            chan = new_rv_channels[i] if i < len(new_rv_channels) else ''
            f    = new_rv_files[i] if i < len(new_rv_files) else None
            if url or f:
                rv = FoodItemRecipeVideo(item=obj, title=title, youtube_channel=chan, video_url=url, order=i)
                if f:
                    rv.video_file = f
                rv.save()
        del_rv = request.POST.getlist('delete_recipe_video')
        if del_rv:
            FoodItemRecipeVideo.objects.filter(pk__in=del_rv, item=obj).delete()

        # Save new growing videos
        new_gv_titles    = request.POST.getlist('new_growing_title')
        new_gv_channels  = request.POST.getlist('new_growing_channel')
        new_gv_urls      = request.POST.getlist('new_growing_url')
        new_gv_files     = request.FILES.getlist('new_growing_file')
        for i, title in enumerate(new_gv_titles):
            url  = new_gv_urls[i]  if i < len(new_gv_urls)  else ''
            chan = new_gv_channels[i] if i < len(new_gv_channels) else ''
            f    = new_gv_files[i] if i < len(new_gv_files) else None
            if url or f:
                gv = FoodItemGrowingVideo(item=obj, title=title, youtube_channel=chan, video_url=url, order=i)
                if f:
                    gv.video_file = f
                gv.save()
        del_gv = request.POST.getlist('delete_growing_video_item')
        if del_gv:
            FoodItemGrowingVideo.objects.filter(pk__in=del_gv, item=obj).delete()

        messages.success(request, 'Item saved.')
        return redirect('hadmin_guide_items')

    import json as _json
    advice = {}
    if obj and obj.condition_advice:
        try:
            advice = _json.loads(obj.condition_advice)
        except Exception:
            advice = {}
    return render(request, 'health/admin/guide_item_edit.html', {
        'obj': obj, 'categories': categories, 'conditions': conditions,
        'advice': advice, 'growing_images': growing_images,
        'recipe_videos': recipe_videos, 'growing_videos': growing_videos,
    })


@super_admin_required
def hadmin_guide_item_delete(request, pk):
    get_object_or_404(FoodItem, pk=pk).delete()
    messages.success(request, 'Item deleted.')
    return redirect('hadmin_guide_items')


# ── FOOD GUIDE USER VIEWS ─────────────────────────────────────────────────────

def guide_home(request):
    items = (FoodItem.objects
             .filter(category__is_active=True)
             .select_related('category')
             .prefetch_related('recipe_videos', 'growing_videos')
             .order_by('category__order', 'order', 'name'))
    items = list(items)
    conditions = list(HealthCondition.objects.all().order_by('name'))
    known_slugs = {condition.slug for condition in conditions}
    for item in items:
        advice = item.get_condition_advice()
        item.condition_slugs = ','.join(sorted(known_slugs.intersection(advice))) if isinstance(advice, dict) else ''
    return render(request, 'health/guide_home.html', {'items': items, 'conditions': conditions})


def guide_category(request, slug):
    category = get_object_or_404(FoodCategory, slug=slug, is_active=True)
    items    = FoodItem.objects.filter(category=category).order_by('order', 'name')
    return render(request, 'health/guide_category.html', {'category': category, 'items': items})


def guide_item(request, cat_slug, item_slug):
    category       = get_object_or_404(FoodCategory, slug=cat_slug)
    item           = get_object_or_404(FoodItem, slug=item_slug, category=category)
    conditions     = HealthCondition.objects.all()
    advice         = item.get_condition_advice()
    if not isinstance(advice, dict):
        advice = {}
    growing_images = item.growing_images.all().order_by('order')
    recipe_videos  = item.recipe_videos.all()
    growing_videos = item.growing_videos.all()
    related        = FoodItem.objects.filter(category=category).exclude(pk=item.pk)[:4]
    return render(request, 'health/guide_item.html', {
        'category': category, 'item': item,
        'show_category_breadcrumb': category.name.strip().casefold() != item.name.strip().casefold(),
        'conditions': conditions, 'advice': advice,
        'growing_images': growing_images, 'related': related,
        'recipe_videos': recipe_videos, 'growing_videos': growing_videos,
    })
