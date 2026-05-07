from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Application, News, HeroSlide, Feature, AboutInfo, CoreValue, ContactInfo
from .forms import ApplicationForm
from core.models import SchoolInfo


def _get_school_info():
    """Helper to get school info for context"""
    school = SchoolInfo.objects.first()
    return school


def _get_contact_info():
    """Helper to get contact info for context"""
    contact = ContactInfo.objects.first()
    return contact


def _get_about_info():
    """Helper to get about info for context"""
    about = AboutInfo.objects.first()
    return about


def home(request):
    school = _get_school_info()
    latest_news = News.objects.filter(is_published=True)[:3]
    hero_slides = HeroSlide.objects.filter(is_active=True)
    features = Feature.objects.filter(is_active=True)
    contact = _get_contact_info()

    # Default hero images (free African/Tanzanian school images from Unsplash)
    default_hero_images = [
        'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=1600&q=80',  # African school children walking
        'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=1600&q=80',  # African students in classroom
        'https://images.unsplash.com/photo-1588072432836-e10032774350?w=1600&q=80',  # African children at desk
        'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1600&q=80',  # Students studying together
        'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=1600&q=80',  # Students in classroom
    ]

    context = {
        'school_info': school,
        'latest_news': latest_news,
        'hero_slides': hero_slides,
        'features': features,
        'contact_info': contact,
        'default_hero_images': default_hero_images,
        'active_page': 'home',
    }

    return render(request, 'website/home.html', context)


def about(request):
    school = _get_school_info()
    about_info = _get_about_info()
    core_values = CoreValue.objects.filter(is_active=True)
    contact = _get_contact_info()
    context = {
        'school_info': school,
        'about_info': about_info,
        'core_values': core_values,
        'contact_info': contact,
        'active_page': 'about',
    }
    return render(request, 'website/about.html', context)


def apply(request):
    school = _get_school_info()
    contact = _get_contact_info()
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been submitted successfully! We will contact you soon.')
            return redirect('website_apply_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ApplicationForm()

    context = {
        'school_info': school,
        'form': form,
        'contact_info': contact,
        'active_page': 'apply',
    }
    return render(request, 'website/apply.html', context)


def apply_success(request):
    school = _get_school_info()
    contact = _get_contact_info()
    context = {
        'school_info': school,
        'contact_info': contact,
        'active_page': 'apply',
    }
    return render(request, 'website/apply_success.html', context)


def news_list(request):
    school = _get_school_info()
    all_news = News.objects.filter(is_published=True)
    contact = _get_contact_info()
    context = {
        'school_info': school,
        'news_list': all_news,
        'contact_info': contact,
        'active_page': 'news',
    }
    return render(request, 'website/news_list.html', context)


def news_detail(request, pk):
    school = _get_school_info()
    news_item = get_object_or_404(News, pk=pk, is_published=True)
    contact = _get_contact_info()
    context = {
        'school_info': school,
        'news_item': news_item,
        'contact_info': contact,
        'active_page': 'news',
    }
    return render(request, 'website/news_detail.html', context)


def contact(request):
    school = _get_school_info()
    contact_info = _get_contact_info()
    context = {
        'school_info': school,
        'contact_info': contact_info,
        'active_page': 'contact',
    }
    return render(request, 'website/contact.html', context)
