from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GalleryImage, SiteContent
from .forms import GalleryImageForm, AboutForm, ContactContentForm

# Keys used in SiteContent
ABOUT_KEYS = [
    'hero_tagline', 'card1_title', 'card1_body', 'card2_title', 'card2_body',
    'card3_title', 'card3_body', 'who_we_are_left', 'who_we_are_right_intro',
    'meeting_nights', 'weekend_sessions', 'cta_body',
]
CONTACT_KEYS = [
    'address_line1', 'address_line2', 'address_line3', 'email',
    'social_handle', 'tuesday_hours', 'thursday_hours', 'sunday_hours', 'maps_url',
]

ABOUT_LABELS = {
    'hero_tagline': 'Hero tagline',
    'card1_title': 'Feature 1 title', 'card1_body': 'Feature 1 text',
    'card2_title': 'Feature 2 title', 'card2_body': 'Feature 2 text',
    'card3_title': 'Feature 3 title', 'card3_body': 'Feature 3 text',
    'who_we_are_left': '"Who We Are" left column',
    'who_we_are_right_intro': '"Who We Are" right intro',
    'meeting_nights': 'Meeting nights', 'weekend_sessions': 'Weekend sessions',
    'cta_body': 'Call-to-action text',
}
CONTACT_LABELS = {
    'address_line1': 'Address line 1', 'address_line2': 'Address line 2',
    'address_line3': 'Address line 3', 'email': 'Email address',
    'social_handle': 'Social media handle',
    'tuesday_hours': 'Tuesday hours', 'thursday_hours': 'Thursday hours',
    'sunday_hours': 'Sunday hours', 'maps_url': 'Google Maps URL',
}

ABOUT_DEFAULTS = {
    'hero_tagline': 'A friendly archery club welcoming archers of all abilities, from complete beginners to experienced competitive shooters.',
    'card1_title': 'Outdoor & Indoor', 'card1_body': 'We shoot year-round — outdoors on our field from spring to autumn, and indoors at our heated facility through the winter months.',
    'card2_title': 'All Bow Styles', 'card2_body': 'Members shoot Recurve, Compound, Barebow, Longbow and more. Our coaches can help you find the style that suits you best.',
    'card3_title': 'Competitive & Social', 'card3_body': "From club shoots and county championships to casual social evenings, there's something for everyone at Beeston Rylands Archers.",
    'who_we_are_left': 'Founded in the heart of the community, Beeston Rylands Archers has been bringing people together through the sport of archery for decades. Our club prides itself on being welcoming, inclusive and passionate about the sport.',
    'who_we_are_right_intro': 'We are affiliated with Archery GB and follow their rules and safety guidelines. All our coaches hold recognised qualifications and our facilities are regularly inspected.',
    'meeting_nights': 'Tuesday & Thursday', 'weekend_sessions': 'Sunday mornings',
    'cta_body': 'Our beginner courses are the perfect way to try archery with no prior experience needed.',
}
CONTACT_DEFAULTS = {
    'address_line1': '123 Archer Lane', 'address_line2': 'Beeston', 'address_line3': 'NG9 1AA',
    'email': 'info@bra-archery.co.uk', 'social_handle': '@BRAArchery',
    'tuesday_hours': '18:30 – 21:00', 'thursday_hours': '18:30 – 21:00',
    'sunday_hours': '09:30 – 12:30', 'maps_url': '',
}


def _get_content(keys, defaults):
    """Return a dict of key→value, falling back to defaults."""
    rows = SiteContent.objects.filter(key__in=keys)
    data = {r.key: r.value for r in rows}
    for k, v in defaults.items():
        data.setdefault(k, v)
    return data


def _save_content(keys, labels, post_data):
    for key in keys:
        value = post_data.get(key, '')
        obj, _ = SiteContent.objects.get_or_create(
            key=key,
            defaults={'label': labels.get(key, key), 'value': value}
        )
        if obj.value != value:
            obj.value = value
            obj.save()


def about(request):
    content = _get_content(ABOUT_KEYS, ABOUT_DEFAULTS)
    return render(request, 'pages/about.html', {'c': content})


@login_required
def about_edit(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('about')
    content = _get_content(ABOUT_KEYS, ABOUT_DEFAULTS)
    if request.method == 'POST':
        _save_content(ABOUT_KEYS, ABOUT_LABELS, request.POST)
        messages.success(request, 'About page updated.')
        return redirect('about')
    form = AboutForm(initial=content)
    return render(request, 'pages/about_edit.html', {'form': form})


def contact(request):
    content = _get_content(CONTACT_KEYS, CONTACT_DEFAULTS)
    sent = False
    if request.method == 'POST':
        sent = True
    return render(request, 'pages/contact.html', {'c': content, 'sent': sent})


@login_required
def contact_edit(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('contact')
    content = _get_content(CONTACT_KEYS, CONTACT_DEFAULTS)
    if request.method == 'POST':
        _save_content(CONTACT_KEYS, CONTACT_LABELS, request.POST)
        messages.success(request, 'Contact page updated.')
        return redirect('contact')
    form = ContactContentForm(initial=content)
    return render(request, 'pages/contact_edit.html', {'form': form})


def gallery(request):
    images = GalleryImage.objects.all()
    return render(request, 'pages/gallery.html', {'images': images})


@login_required
def gallery_upload(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('gallery')
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.uploaded_by = request.user
            img.save()
            messages.success(request, 'Photo uploaded.')
            return redirect('gallery')
    else:
        form = GalleryImageForm()
    return render(request, 'pages/gallery_upload.html', {'form': form})


@login_required
def gallery_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('gallery')
    img = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        img.image.delete(save=False)
        img.delete()
        messages.success(request, 'Photo deleted.')
    return redirect('gallery')
