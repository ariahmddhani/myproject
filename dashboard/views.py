from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
import requests
from django.shortcuts import get_object_or_404
from .models import *
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate ,login, logout
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from django.conf import settings
import os
from django.core.exceptions import SuspiciousFileOperation
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Case, When, IntegerField
import json


def is_admin(user):
    return user.is_superuser


def pengaduan_partial(request):
    aduans = PengaduanAsing.objects.annotate(jumlah_jawaban=Count('jawaban_set'))
    return render(request, 'backend/pengaduanasing_tbody.html', {'aduans': aduans})

@login_required
def dashboard(request):
    template_name = "backend/dashboard.html"
    
    # Data User
    total_users = User.objects.count()
    
    # Data yang diinput user (pendaftaran / pengajuan)
    total_suket_rek_kel_tani = SuketRekKelTani.objects.count()   # besukan online
    total_aduan = PengaduanAsing.objects.count()                # pengaduan
    total_ilb = IjinLuarBiasa.objects.count()                   # ijin luar biasa
    total_bantuan_hukum = BantuanHukum.objects.count()          # bantuan hukum

    # Data chart (tanpa user)
    chart_varian = ["Besukan", "Pengaduan", "ILB", "Bantuan Hukum"]
    chart_variasi = [
        total_suket_rek_kel_tani,
        total_aduan,
        total_ilb,
        total_bantuan_hukum
    ]

    chart_labels = ["Review", "Disetujui", "Ditolak"]
    chart_values = [
        SuketRekKelTani.objects.filter(status="review").count(),
        SuketRekKelTani.objects.filter(status="approved").count(),
        SuketRekKelTani.objects.filter(status="rejected").count(),
    ]


    total_review = SuketRekKelTani.objects.filter(status='review').count()
    total_acc = SuketRekKelTani.objects.filter(status='approved').count()
    total_reject = SuketRekKelTani.objects.filter(status='rejected').count()
    # Artikel / pengumuman
    blg = Blog.objects.all().order_by('-id')[:5]
    annc = Pengumuman.objects.all().order_by('-id')[:5]
    pangan = BeritaKetahananPangan.objects.all().order_by('-id')[:5]

    # Recent Surat (contoh dari SuketRekKelTani)
    suket_rek_kel_tani = SuketRekKelTani.objects.all().order_by('-date')
    recent_surat = [
        {'surat': surat, 'type': 'Pendaftaran Besukan'}
        for surat in suket_rek_kel_tani
    ]
    recent_surat = sorted(recent_surat, key=lambda x: x['surat'].date, reverse=True)

    # Context
    context = {
        'title': 'Dashboard',
        'total_users': total_users,
        'total_suket_rek_kel_tani': total_suket_rek_kel_tani,
        'total_aduan': total_aduan,
        'total_ilb': total_ilb,
        'total_bantuan_hukum': total_bantuan_hukum,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'chart_varian': chart_varian,
        'chart_variasi': chart_variasi,
        'recent_surat': recent_surat,
        "total_review": total_review,
        "total_acc": total_acc,
        "total_reject": total_reject,
        'blg': blg,
        'annc': annc,
        'pangan': pangan,
        'allow_tambah_surat': get_allow_tambah_surat(),
    }
    
    return render(request, template_name, context)


import json
from django.db.models import Case, When, IntegerField
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def suketrekkeltani(request):
    template_name = "backend/pendaftaran.html"

    pengaturan, _ = Pengaturan.objects.get_or_create(id=1)

    if request.method == "POST":
        # Cek apakah pendaftaran diizinkan
        if not pengaturan.allow_tambah_surat and not request.user.is_superuser:
            return redirect('suketrekkeltani')

        # --- Ambil barang bawaan dari form ---
        barang_list = []
        for i in range(1, 7):  # sesuai jumlah input di template
            nama = request.POST.get(f"barang_nama_{i}")
            jumlah = request.POST.get(f"barang_jumlah_{i}")
            satuan = request.POST.get(f"barang_satuan_{i}")
            if nama and jumlah:  # hanya simpan kalau ada nama dan jumlah
                try:
                    jumlah_int = int(jumlah)
                except ValueError:
                    jumlah_int = 0
                barang_list.append({
                    "nama": nama,
                    "jumlah": jumlah_int,
                    "satuan": satuan or ""
                })

        # --- Simpan Surat Keterangan ---
        suket = SuketRekKelTani.objects.create(
            penulis=request.user,
            nama=request.POST.get("inputNama"),
            email=request.POST.get("inputEmail"),
            telepon=request.POST.get("inputNotelp"),
            ktp=request.POST.get("inputKTP"),
            ttl=request.POST.get("inputTTL"),
            alamat=request.POST.get("inputAlamat"),
            namawbp=request.POST.get("inputnamawbp"),
            hubungan=request.POST.get("inputHubungan"),
            tanggal_kunjungan=request.POST.get("inputTanggal"),
            jam_kunjungan=request.POST.get("inputJam"),
            jenis_kunjungan=request.POST.get("inputJenis"),

            pengikut_laki=int(request.POST.get("pengikut_laki", 0)),
            pengikut_perempuan=int(request.POST.get("pengikut_perempuan", 0)),
            pengikut_anak=int(request.POST.get("pengikut_anak", 0)),

            barang_bawaan=json.dumps(barang_list, ensure_ascii=False),  # simpan JSON string
            status='review'
        )

        # --- Simpan data pengikut ---
        for i in range(suket.pengikut_laki):
            nama = request.POST.get(f"pengikut_laki_nama_{i}")
            nik = request.POST.get(f"pengikut_laki_nik_{i}")
            if nama:
                Pengikut.objects.create(suket=suket, nama=nama, nik=nik, kategori="laki")

        for i in range(suket.pengikut_perempuan):
            nama = request.POST.get(f"pengikut_perempuan_nama_{i}")
            nik = request.POST.get(f"pengikut_perempuan_nik_{i}")
            if nama:
                Pengikut.objects.create(suket=suket, nama=nama, nik=nik, kategori="perempuan")

        for i in range(suket.pengikut_anak):
            nama = request.POST.get(f"pengikut_anak_nama_{i}")
            nik = request.POST.get(f"pengikut_anak_nik_{i}")
            if nama:
                Pengikut.objects.create(suket=suket, nama=nama, nik=nik, kategori="anak")

        return redirect('suketrekkeltani')

    # --- List Data ---
    if request.user.is_superuser:
        suket_list = SuketRekKelTani.objects.annotate(
            priority=Case(
                When(status='review', then=0),
                default=1,
                output_field=IntegerField()
            )
        ).order_by('priority', '-tanggal_kunjungan')
    else:
        suket_list = SuketRekKelTani.objects.filter(
            penulis=request.user
        ).order_by('-tanggal_kunjungan')

    # --- Parse JSON barang_bawaan supaya bisa ditampilkan di template ---
    for s in suket_list:
        try:
            s.barang_bawaan = json.loads(s.barang_bawaan) if s.barang_bawaan else []
        except Exception:
            s.barang_bawaan = []

    context = {
        "suket": suket_list,
        "allow_tambah_surat": pengaturan.allow_tambah_surat,
    }
    return render(request, template_name, context)



@property
def total_pengikut(self):
    return self.pengikut_laki + self.pengikut_perempuan + self.pengikut_anak

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import SuketRekKelTani, Pengikut


@login_required
def edit_suketrekkeltani(request, id):
    surat = get_object_or_404(SuketRekKelTani, id=id)

    if request.method == "POST":
        # update field utama
        surat.nama = request.POST.get("nama")
        surat.email = request.POST.get("email")
        surat.telepone = request.POST.get("telepon")
        surat.ktp = request.POST.get("ktp")
        surat.ttl = request.POST.get("ttl")
        surat.alamat = request.POST.get("alamat")
        surat.namawbp = request.POST.get("namawbp")
        surat.hubungan = request.POST.get("hubungan")
        surat.tanggal_kunjungan = request.POST.get("tanggal_kunjungan")
        surat.jam_kunjungan = request.POST.get("jam_kunjungan")
        surat.jenis_kunjungan = request.POST.get("jenis_kunjungan")

        # ==========================
        # 1. Simpan Barang Bawaan
        # ==========================
        barang_list = []
        for i in range(1, 7):  # karena di template ada 6 row
            nama = request.POST.get(f"barang_nama_{i}")
            jumlah = request.POST.get(f"barang_jumlah_{i}")
            satuan = request.POST.get(f"barang_satuan_{i}")

            if nama and jumlah and satuan:
                barang_list.append({
                    "nama": nama,
                    "jumlah": jumlah,
                    "satuan": satuan
                })

        surat.barang_bawaan = json.dumps(barang_list, ensure_ascii=False)

        surat.save()

        # ==========================
        # 2. Update Pengikut Lama
        # ==========================
        for p in surat.pengikut.all():
            nama = request.POST.get(f"pengikut_nama_{p.id}")
            nik = request.POST.get(f"pengikut_nik_{p.id}")
            kategori = request.POST.get(f"pengikut_kategori_{p.id}")
            if nama and nik:
                p.nama = nama
                p.nik = nik
                p.kategori = kategori
                p.save()

        # ==========================
        # 3. Tambah Pengikut Baru
        # ==========================
        for i in range(1, 7):  # sesuai jumlah row kosong di template
            nama = request.POST.get(f"pengikut_nama_new{i}")
            nik = request.POST.get(f"pengikut_nik_new{i}")
            kategori = request.POST.get(f"pengikut_kategori_new{i}")

            if nama and nik:
                Pengikut.objects.create(
                    suket=surat,
                    nama=nama,
                    nik=nik,
                    kategori=kategori
                )

        return redirect("suketrekkeltani")

    # ubah barang_bawaan JSON string jadi list biar bisa di-loop di template
    try:
        barang_list = json.loads(surat.barang_bawaan)
    except:
        barang_list = []

    context = {
        "surat": surat,
        "barang_list": barang_list,
    }

    return render(request, "backend/edit_suketrekkeltani.html", context)

@login_required
@user_passes_test(is_admin)
def setujui_suketrekeltani(request, id):
    if request.user.is_superuser:
        suket = get_object_or_404(SuketRekKelTani, id=id)
        suket.status = 'approved'  # Mengubah status menjadi Disetujui
        suket.save()
    return redirect('suketrekkeltani')  # Redirect ke halaman list Suket Rek Kel Tani


@login_required
@user_passes_test(is_admin)
def tolak_suketrekeltani(request, id):
    if request.user.is_superuser:
        suket = get_object_or_404(SuketRekKelTani, id=id)
        if request.method == "POST":
            catatan = request.POST.get("catatan_admin", "")
            suket.catatan_admin = catatan
            suket.status = "rejected"
            suket.save()

            # Kirim email otomatis ke pemohon
            if suket.email:  
                subject = "Permohonan Besukan Anda Ditolak"
                message = (
                    f"Halo {suket.nama},\n\n"
                    f"Permohonan besukan Anda dengan ID #{suket.id} telah DITOLAK.\n\n"
                    f"Catatan dari admin:\n{catatan}\n\n"
                    f"Silakan periksa kembali data permohonan Anda di sistem."
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # pastikan di settings.py ada DEFAULT_FROM_EMAIL
                    [suket.email],
                    fail_silently=False,
                )

    return redirect("suketrekkeltani")

@login_required
def delete_suketrekkeltani(request, id):
    SuketRekKelTani.objects.get(id=id).delete()
    return redirect('suketrekkeltani')

@login_required
def print_suketrekkeltani(request, id):
    template_name = "surat/surat-rekomendasi-kelompok-tani.html"
    surat = get_object_or_404(SuketRekKelTani, id=id)

    # Hitung total pengikut
    total_pengikut = (
        (surat.pengikut_laki or 0) +
        (surat.pengikut_perempuan or 0) +
        (surat.pengikut_anak or 0)
    )

    # Parse barang bawaan (supaya bisa di-loop di template)
    try:
        surat.barang_bawaan = json.loads(surat.barang_bawaan) if surat.barang_bawaan else []
    except Exception:
        surat.barang_bawaan = []

    context = {
        "suket": surat,
        "total_pengikut": total_pengikut,
    }
    return render(request, template_name, context)




@login_required
def detail_suketrekkeltani(request, id):
    template_name = "backend/detailpendaftar.html"

    suket = get_object_or_404(SuketRekKelTani, id=id)

    # hitung jumlah pengikut berdasarkan kategori
    pengikut = suket.pengikut.all()
    laki = pengikut.filter(kategori__iexact="laki").count()
    perempuan = pengikut.filter(kategori__iexact="perempuan").count()
    anak = pengikut.filter(kategori__iexact="anak-anak").count()
    total = pengikut.count()

    context = {
        'suket': suket,
        'jumlah_laki': laki,
        'jumlah_perempuan': perempuan,
        'jumlah_anak': anak,
        'total_pengikut': total,
    }

    return render(request, template_name, context)



@login_required
def pengumuman(request):
    template_name = "backend/pengumuman.html"
    
    annc = Pengumuman.objects.all()
    
    if request.method == 'POST':
        judul = request.POST.get("inputJudul")
        konten = request.POST.get("inputKonten")
        picture = request.FILES.get("inputGambar")
        
        fs = FileSystemStorage()

        def save_file(uploaded_file):
            if uploaded_file:
                # Mengganti spasi dengan underscore pada nama file
                filename = uploaded_file.name.replace(" ", "_")
                return fs.save(filename, uploaded_file), fs.url(filename)
            return None, None

        # Jika ada file gambar yang di-upload
        picture_filename, url_pengantar = save_file(picture)

        Pengumuman.objects.create(
            penulis=request.user,
            judul=judul,
            konten=konten,
            picture=url_pengantar
        )
        
        return redirect('pengumuman')
        
    context = {
        "annc": annc
    }
    
    return render(request, template_name, context)

@login_required
def edit_pengumuman(request, id):
    template_name = "backend/pengumuman.html"
    
    pengumuman_id = Pengumuman.objects.get(id=id)
    
    if request.method == "POST":
        # Mengambil input data dari form
        judul = request.POST.get("inputJudul")
        konten = request.POST.get("inputKonten")
        picture = request.FILES.get("inputGambar")
        
        fs = FileSystemStorage()

        def save_file(uploaded_file):
            if uploaded_file:
                # Mengganti spasi dengan underscore pada nama file
                filename = uploaded_file.name.replace(" ", "_")
                return fs.save(filename, uploaded_file), fs.url(filename)
            return None, None

        # Jika ada file gambar baru yang di-upload
        if picture:
            picture_filename, url_pengantar = save_file(picture)
            pengumuman_id.picture = url_pengantar
        
        # Update data di objek pengumuman
        pengumuman_id.judul = judul
        pengumuman_id.konten = konten
        pengumuman_id.date = timezone.now()

        pengumuman_id.save()
        
        return redirect('pengumuman')  # Redirect ke halaman pengumuman (sesuaikan dengan rute yang kamu inginkan)
    
    context = {
        "value": pengumuman_id
    }
    
    return render(request, template_name, context)

@login_required
def delete_pengumuman(request, id):
    Pengumuman.objects.get(id=id).delete()
    return redirect('pengumuman')  # Redirect ke halaman pengumuman (sesuaikan dengan rute yang kamu inginkan)


@login_required
def berita_ketahanan_pangan(request):
    template_name = "backend/ketahananpangan.html"
    
    berita = BeritaKetahananPangan.objects.all().order_by("-id")
    
    if request.method == 'POST':
        judul = request.POST.get("inputJudul")
        konten = request.POST.get("inputKonten")
        picture = request.FILES.get("inputGambar")
        
        fs = FileSystemStorage()

        def save_file(uploaded_file):
            if uploaded_file:
                filename = uploaded_file.name.replace(" ", "_")  # ganti spasi
                return fs.save(filename, uploaded_file), fs.url(filename)
            return None, None

        # simpan file gambar
        picture_filename, url_gambar = save_file(picture)

        # simpan ke DB
        BeritaKetahananPangan.objects.create(
            judul=judul,
            isi=konten,
            gambar=url_gambar
        )
        
        return redirect('berita_ketahanan_pangan')
        
    context = {
        "berita": berita
    }
    
    return render(request, template_name, context)

@login_required
def edit_berita_ketahanan_pangan(request, id):
    berita = get_object_or_404(BeritaKetahananPangan, id=id)
    template_name = "backend/ketahananpangan.html"

    if request.method == "POST":
        judul = request.POST.get("inputJudul")
        konten = request.POST.get("inputKonten")
        picture = request.FILES.get("inputGambar")

        fs = FileSystemStorage()

        if picture:  # kalau ada upload gambar baru
            filename = picture.name.replace(" ", "_")
            picture_filename = fs.save(filename, picture)
            url_gambar = fs.url(picture_filename)
            berita.gambar = url_gambar  # update gambar

        berita.judul = judul
        berita.isi = konten
        berita.save()

        return redirect("berita_ketahanan_pangan")

    context = {
    "value": berita,   # untuk form edit
    "berita": BeritaKetahananPangan.objects.all()  # untuk list tabel
}

    return render(request, template_name, context)

@login_required
def delete_berita_ketahanan_pangan(request, id):
    BeritaKetahananPangan.objects.get(id=id).delete()
    return redirect('berita_ketahanan_pangan')  # Redirect ke halaman pengumuman (sesuaikan dengan rute yang kamu inginkan)



@login_required    
def blog(request):
    template_name = "backend/blog.html"
    
    blg = Blog.objects.all()
    
    if request.method == 'POST':
        judul = request.POST.get("inputJudul")
        konten = request.POST.get("inputKonten")
        picture = request.FILES.get("inputGambar")
        
        fs = FileSystemStorage()

        def save_file(uploaded_file):
            if uploaded_file:
                # Mengganti spasi dengan underscore pada nama file
                filename = uploaded_file.name.replace(" ", "_")
                return fs.save(filename, uploaded_file), fs.url(filename)
            return None, None

        # Jika ada file gambar yang di-upload
        picture_filename, url_pengantar = save_file(picture)

        Blog.objects.create(
            penulis=request.user,
            judul=judul,
            konten=konten,
            picture=url_pengantar
        )
        
        return redirect('blog')
        
    context = {
        "blg": blg,
        "title": "Halaman Berita"
    }
    
    return render(request, template_name, context)

@login_required
def edit_blog(request, id):
    template_name = "backend/blog.html"
    
    blog_id = Blog.objects.get(id=id)
    
    if request.method == "POST":
        # Mengambil input data dari form
        judul = request.POST.get("inputJudul")
        konten = request.POST.get("inputKonten")
        picture = request.FILES.get("inputGambar")
        
        fs = FileSystemStorage()

        def save_file(uploaded_file):
            if uploaded_file:
                # Mengganti spasi dengan underscore pada nama file
                filename = uploaded_file.name.replace(" ", "_")
                return fs.save(filename, uploaded_file), fs.url(filename)
            return None, None

        # Jika ada file gambar baru yang di-upload
        if picture:
            picture_filename, url_pengantar = save_file(picture)
            blog_id.picture = url_pengantar
        
        # Update data di objek blog
        blog_id.judul = judul
        blog_id.konten = konten
        blog_id.date = timezone.now()

        blog_id.save()
        
        return redirect('blog')  # Redirect ke halaman blog (sesuaikan dengan rute yang kamu inginkan)
    
    context = {
        "value": blog_id
    }
    
    return render(request, template_name, context)

@login_required
def delete_blog(request, id):
    Blog.objects.get(id=id).delete()
    return redirect('blog')  # Redirect ke halaman pengumuman (sesuaikan dengan rute yang kamu inginkan)

@login_required
def detail_blog(request, id):
    template_name = "backend/detailblog.html"
    
    blg = Blog.objects.get(id=id)
    
    context = {
        "blg" : blg
    }
    
    return render (request, template_name, context)

@login_required
def logoutPage(request):
    logout(request)
    return redirect('welcome')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        nik = request.POST['nik']
        ktp = request.FILES['ktp']

        # Validasi password
        if password != password2:
            return render(request, 'backend/register.html', {'error': 'Passwords do not match'})
        
        # Validasi apakah NIK sudah ada di database
        if Profile.objects.filter(nik=nik).exists():
            return render(request, 'backend/register.html', {'error': 'NIK already exists'})

        # Validasi apakah username sudah ada di database
        if User.objects.filter(username=username).exists():
            return render(request, 'backend/register.html', {'error': 'Username already exists'})
        
        # Buat user baru
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        # Menyimpan KTP dengan mengganti spasi dengan underscore
        fs = FileSystemStorage()
        ktp_filename = ktp.name.replace(" ", "_")  # Mengganti spasi dengan underscore
        filename = fs.save(ktp_filename, ktp)
        ktp_url = fs.url(filename)

        # Update profil pengguna dengan NIK dan KTP
        user.profile.nik = nik
        user.profile.ktp = ktp_url
        user.profile.save()

        # Login otomatis setelah registrasi
        login(request, user)

        return redirect('dashboard')  # Redirect ke halaman utama setelah registrasi

    return render(request, 'backend/register.html')

@login_required
def profile(request):
    template_name = "backend/profile.html"
     # Ambil user yang sedang login
    user = request.user

    # Ambil profil terkait user
    profile = Profile.objects.get(user=user)
    
    context = {
        "user":user,
        "profile" : profile,
    }
    
    
    return render(request,template_name, context)

@login_required
@user_passes_test(is_admin)
def daftaruser(request):
    template_name = "backend/daftaruser.html"
   
    profile = Profile.objects.all()
    
    context = {
        "profile":profile,
     
    }
    return render(request,template_name, context)

@login_required
@user_passes_test(is_admin)
def detailuser(request,id):
    template_name = "backend/detailuser.html"
   
    user = get_object_or_404(User, id=id)
    profile = user.profile
    
    context = {
        "profile":profile,
     
    }
    
    return render(request,template_name, context)

@login_required
@user_passes_test(is_admin)
def hapususers(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect(daftaruser)

@login_required
@user_passes_test(is_admin)
def edituser(request, id):
    # Mengambil objek user dan profil berdasarkan ID
    user = get_object_or_404(User, id=id)
    profile = user.profile

    if request.method == 'POST':
        # Mengambil data dari form
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        nik = request.POST['nik']

        # Mengambil file KTP yang diupload (jika ada)
        if 'ktp' in request.FILES:
            ktp = request.FILES['ktp']
            # Ganti spasi dengan underscore pada nama file
            ktp.name = ktp.name.replace(' ', '_')
            fs = FileSystemStorage()
            filename = fs.save(ktp.name, ktp)
            ktp_url = fs.url(filename)
            profile.ktp = ktp_url  # Update KTP jika ada

        # Update data user
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update data profil
        profile.nik = nik
        profile.save()

        # Redirect setelah penyimpanan
        return redirect('daftar_user')  # Redirect ke halaman detail user setelah update

    # Jika requestnya GET, tampilkan form dengan data user yang sudah ada
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'backend/edituser.html', context)

@login_required
@user_passes_test(is_admin)
def datapengaduanasing(request):
    template_name = "backend/pengaduanasing.html"
   
    aduan = PengaduanAsing.objects.all()
    
    context = {
        "aduans":aduan,
     
    }
    return render(request,template_name, context)


@login_required
@user_passes_test(is_admin)
def detailpengaduanasing(request, id):
    aduan = get_object_or_404(PengaduanAsing, id=id)
    riwayat_jawaban = JawabanPengaduanAsing.objects.filter(pengaduan=aduan).order_by('-tanggal')

    if request.method == "POST":
        jawaban_text = request.POST.get('jawaban')
        if jawaban_text:
            JawabanPengaduanAsing.objects.create(
                pengaduan=aduan,
                jawaban=jawaban_text,
                tanggal=timezone.now(),
                dijawab_oleh=request.user
            )

            # ✅ Kirim email ke pengirim pengaduan
            send_mail(
                subject="Balasan atas pengaduan Anda",
                message=f"Yth. {aduan.name},\n\nBerikut jawaban dari pengaduan Anda:\n\n{jawaban_text}\n\nTerima kasih.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[aduan.email],
                fail_silently=False,
            )

            messages.success(request, "Jawaban berhasil dikirim dan disimpan.")
            return redirect('detail_pengaduan_asing', id=aduan.id)

    return render(request, 'backend/detailpengaduanasing.html', {
        'aduans': aduan,
        'riwayat_jawaban': riwayat_jawaban
    })

from django.db.models import Count


@login_required
@user_passes_test(is_admin)
def datapengaduanasing(request):
    aduans = PengaduanAsing.objects.annotate(jumlah_jawaban=Count('jawaban_set'))


    return render(request, 'backend/pengaduanasing.html', {'aduans': aduans})



@login_required
@user_passes_test(is_admin)
def deletepengaduanasing(request,id):
    datas = PengaduanAsing.objects.get(id=id)
    datas.delete()
    return redirect(datapengaduanasing)

@login_required
@user_passes_test(is_admin)
def arsip_pengaduan_asing(request, id):
    # Ambil objek berdasarkan ID atau 404 jika tidak ditemukan
    data = get_object_or_404(PengaduanAsing, id=id)

    # Pindahkan ke model arsip
    PengaduanAsingArsip.objects.create(
        name=data.name,
        email=data.email,
        phone=data.phone,
        ktp=data.ktp,
        message=data.message,
    )

    # Hapus data dari tabel utama
    data.delete()

    # Redirect kembali ke halaman daftar pengaduan
    return redirect(datapengaduanasing)

@login_required
@user_passes_test(is_admin)
def daftar_arsip_pengaduan_asing(request):
    arsip_list = PengaduanAsingArsip.objects.all()
    return render(request, 'backend/arsip.html', {'arsips': arsip_list})

from django.shortcuts import render, get_object_or_404

@login_required
@user_passes_test(is_admin)
def detail_arsip_pengaduan_asing(request, id):
    aduans = get_object_or_404(PengaduanAsingArsip, id=id)
    return render(request, 'backend/detailarsip.html', {'aduans': aduans})



@login_required
@user_passes_test(is_admin)
def register_super_admin(request):
    if request.method == 'POST':
        # Ambil data dari form POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validasi password cocok
        if password1 != password2:
            return render(request, 'backend/register_super_admin.html', {
                'error': 'Passwords do not match'
            })

        # Cek apakah username sudah ada
        if User.objects.filter(username=username).exists():
            return render(request, 'backend/register_super_admin.html', {
                'error': 'Username already exists'
            })

        # Membuat super admin baru
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = True  # Beri hak akses superuser
        user.is_staff = True  # Beri akses admin dashboard
        user.save()

        return redirect('dashboard')  # Redirect setelah registrasi berhasil

    return render(request, 'backend/register_super_admin.html')

# LIST & FORM

@login_required
def ijinluarbiasa(request):
    if request.method == "POST":
        IjinLuarBiasa.objects.create(
            penulis=request.user,
            nama_pengaju=request.POST.get("nama_pengaju"),
            ktp_pengaju=request.POST.get("ktp_pengaju"),
            alamat_pengaju=request.POST.get("alamat_pengaju"),
            hubungan=request.POST.get("hubungan"),
            nama_wbp=request.POST.get("nama_wbp"),
            register_wbp=request.POST.get("register_wbp"),
            jenis_izin=request.POST.get("jenis_izin"),
            alasan=request.POST.get("alasan"),
            tanggal_ijin=request.POST.get("tanggal_ijin"),
            durasi=request.POST.get("durasi"),

            dokumen_ktp_kk=request.FILES.get("dokumen_ktp_kk"),
            dokumen_pernyataan=request.FILES.get("dokumen_pernyataan"),
            dokumen_keterangan_desa=request.FILES.get("dokumen_keterangan_desa"),
            dokumen_sakit=request.FILES.get("dokumen_sakit"),
            dokumen_kematian_rt=request.FILES.get("dokumen_kematian_rt"),
            dokumen_waris=request.FILES.get("dokumen_waris"),
        )
        return redirect("ijinluarbiasa")

    if request.user.is_superuser:
        data_ilb = IjinLuarBiasa.objects.all().order_by("-tanggal_pengajuan")
    else:
        data_ilb = IjinLuarBiasa.objects.filter(penulis=request.user).order_by("-tanggal_pengajuan")

    return render(request, "backend/ijinluarbiasa.html", {
        "form_mode": "list",
        "data_ilb": data_ilb
    })


@login_required
def edit_ilb(request, id):
    ilb = get_object_or_404(IjinLuarBiasa, id=id)

    if request.method == "POST":
        data = request.POST
        files = request.FILES

        ilb.nama_pengaju = data.get("nama_pengaju")
        ilb.ktp_pengaju = data.get("ktp_pengaju")
        ilb.alamat_pengaju = data.get("alamat_pengaju")
        ilb.hubungan = data.get("hubungan")
        ilb.nama_wbp = data.get("nama_wbp")
        ilb.register_wbp = data.get("register_wbp")
        ilb.jenis_izin = data.get("jenis_izin")
        ilb.alasan = data.get("alasan")
        ilb.tanggal_ijin = data.get("tanggal_ijin")
        ilb.durasi = data.get("durasi")

        if files.get("dokumen_ktp_kk"): ilb.dokumen_ktp_kk = files.get("dokumen_ktp_kk")
        if files.get("dokumen_pernyataan"): ilb.dokumen_pernyataan = files.get("dokumen_pernyataan")
        if files.get("dokumen_keterangan_desa"): ilb.dokumen_keterangan_desa = files.get("dokumen_keterangan_desa")
        if files.get("dokumen_sakit"): ilb.dokumen_sakit = files.get("dokumen_sakit")
        if files.get("dokumen_kematian_rt"): ilb.dokumen_kematian_rt = files.get("dokumen_kematian_rt")
        if files.get("dokumen_waris"): ilb.dokumen_waris = files.get("dokumen_waris")

        ilb.save()
        return redirect("ijinluarbiasa")

    return render(request, "backend/ilb_form.html", {"ilb": ilb})

@login_required
def detaililb(request, id):
    template_name = "backend/detailijinluarbiasa.html"  # Template untuk halaman detail
    
    # Mengambil objek SuketRekKelTani berdasarkan ID
    ilb = get_object_or_404(IjinLuarBiasa, id=id)
    
    # Mengirim data ke template
    context = {
        'ilb': ilb,
    }
    
    return render(request, template_name, context)

# DELETE DATA
@login_required
def delete_ilb(request, id):
    ilb = get_object_or_404(IjinLuarBiasa, id=id)
    ilb.delete()
    return redirect("ijinluarbiasa")


# SETUJUI
@login_required
@user_passes_test(is_admin)
def setujui_ilb(request, id):
    ilb = get_object_or_404(IjinLuarBiasa, id=id)
    ilb.status = "disetujui"
    ilb.save()
    messages.success(request, f'Pengajuan ILB {ilb.nama_pengaju} berhasil disetujui.')
    return redirect("ijinluarbiasa")



@login_required
@user_passes_test(is_admin)
def tolak_ilb(request, id):
    if request.method == 'POST':
        ilb = get_object_or_404(IjinLuarBiasa, id=id)
        # ambil pesan penolakan dari form
        pesan = request.POST.get('pesan_penolakan')
        ilb.catatan_admin = pesan
        ilb.status = 'ditolak'
        ilb.save()
        messages.success(request, f'Pengajuan ILB {ilb.nama_pengaju} berhasil ditolak.')
    return redirect('ijinluarbiasa')

# CETAK SURAT
@login_required
def print_ilb(request, id):
    ilb = get_object_or_404(IjinLuarBiasa, id=id)
    if ilb.status != "approved":
        return HttpResponse("Surat hanya bisa dicetak jika sudah disetujui.")
    return render(request, "backend/ilb_surat.html", {"ilb": ilb})


@login_required
def bantuan_hukum(request):
    if request.method == "POST":
        BantuanHukum.objects.create(
            penulis=request.user,
            nama_pengaju=request.POST.get("nama_pengaju"),
            ktp_pengaju=request.POST.get("ktp_pengaju"),
            alamat_pengaju=request.POST.get("alamat_pengaju"),
            hubungan=request.POST.get("hubungan"),
            no_hp=request.POST.get("no_hp"),
            pekerjaan_pengaju=request.POST.get("pekerjaan_pengaju"),
            nama_wbp=request.POST.get("nama_wbp"),
            blok_wbp=request.POST.get("blok_wbp"),
            pasal=request.POST.get("pasal"),
            lama_hukuman=request.POST.get("lama_hukuman"),
            kategori_permasalahan=request.POST.get("kategori_permasalahan"),
            kronologi=request.POST.get("kronologi"),
            jenis_bantuan=request.POST.get("jenis_bantuan"),
            dokumen_ktp_kk=request.FILES.get("dokumen_ktp_kk"),
            dokumen_surat_kuasa=request.FILES.get("dokumen_surat_kuasa"),
            dokumen_sktm=request.FILES.get("dokumen_sktm"),
            dokumen_putusan=request.FILES.get("dokumen_putusan"),
            dokumen_lainnya=request.FILES.get("dokumen_lainnya"),
        )
        return redirect("bantuan_hukum")

    if request.user.is_superuser:
        data_bh = BantuanHukum.objects.all().order_by("-tanggal_pengajuan")
    else:
        data_bh = BantuanHukum.objects.filter(penulis=request.user).order_by("-tanggal_pengajuan")

    return render(request, "backend/bantuanhukum.html", {
        "data_bh": data_bh
    })


# DETAIL
@login_required
def detail_bantuan_hukum(request, id):
    bh = get_object_or_404(BantuanHukum, id=id)
    return render(request, "backend/detailbantuanhukum.html", {"bh": bh})


# EDIT
@login_required
def edit_bantuan_hukum(request, id):
    bh = get_object_or_404(BantuanHukum, id=id)

    if request.method == "POST":
        data = request.POST
        files = request.FILES

        # update field text
        bh.nama_pengaju = data.get("nama_pengaju")
        bh.ktp_pengaju = data.get("ktp_pengaju")
        bh.alamat_pengaju = data.get("alamat_pengaju")
        bh.hubungan = data.get("hubungan")
        bh.no_hp = data.get("no_hp")
        bh.pekerjaan_pengaju = data.get("pekerjaan_pengaju")
        bh.nama_wbp = data.get("nama_wbp")
        bh.blok_wbp = data.get("blok_wbp")
        bh.pasal = data.get("pasal")
        bh.lama_hukuman = data.get("lama_hukuman")
        bh.kategori_permasalahan = data.get("kategori_permasalahan")
        bh.kronologi = data.get("kronologi")
        bh.jenis_bantuan = data.get("jenis_bantuan")

        # update dokumen hanya jika user upload file baru
        if files.get("dokumen_ktp_kk"):
            bh.dokumen_ktp_kk = files.get("dokumen_ktp_kk")
        if files.get("dokumen_surat_kuasa"):
            bh.dokumen_surat_kuasa = files.get("dokumen_surat_kuasa")
        if files.get("dokumen_sktm"):
            bh.dokumen_sktm = files.get("dokumen_sktm")
        if files.get("dokumen_putusan"):
            bh.dokumen_putusan = files.get("dokumen_putusan")
        if files.get("dokumen_lainnya"):
            bh.dokumen_lainnya = files.get("dokumen_lainnya")

        bh.save()
        return redirect("bantuan_hukum")

    # kalau GET → tampilkan form edit
    return render(request, "backend/bantuanhukum.html", {
        "form_mode": "edit",
        "bh": bh,
    })

# DELETE
@login_required
def delete_bantuan_hukum(request, id):
    bh = get_object_or_404(BantuanHukum, id=id)
    bh.delete()
    return redirect("bantuan_hukum")


# SETUJUI
@login_required
@user_passes_test(is_admin)
def setuju_bantuan_hukum(request, id):
    bh = get_object_or_404(BantuanHukum, id=id)
    bh.status = "approved"
    bh.save()
    return redirect("bantuan_hukum")


# TOLAK
@login_required
@user_passes_test(is_admin)
def tolak_bantuan_hukum(request, id):
    if request.method == "POST":
        bh = get_object_or_404(BantuanHukum, id=id)
        pesan = request.POST.get("pesan_penolakan")
        bh.catatan_admin = pesan
        bh.status = "rejected"
        bh.save()
        messages.success(request, f"Pengajuan Bantuan Hukum {bh.nama_pengaju} berhasil ditolak.")
    return redirect("bantuan_hukum")



@login_required
def dokumen_integrasi(request):
    if request.method == "POST":
        judul = request.POST.get("judul")
        deskripsi = request.POST.get("deskripsi")
        file = request.FILES.get("file")

        if judul and file:
            DokumenIntegrasi.objects.create(
                judul=judul,
                deskripsi=deskripsi,
                file=file,
            )
        return redirect("dokumen_integrasi")

    dokumen_list = DokumenIntegrasi.objects.all().order_by("-tanggal_upload")
    return render(request, "backend/integrasi.html", {"dokumen_list": dokumen_list})


@login_required
def edit_dokumen_integrasi(request, id):
    dokumen = get_object_or_404(DokumenIntegrasi, id=id)
    if request.method == "POST":
        dokumen.judul = request.POST.get("judul")
        dokumen.deskripsi = request.POST.get("deskripsi")
        if request.FILES.get("file"):
            dokumen.file = request.FILES["file"]
        dokumen.save()
        return redirect("dokumen_integrasi")
    return redirect("dokumen_integrasi")

@login_required
def delete_dokumen_integrasi(request, id):
    dokumen = get_object_or_404(DokumenIntegrasi, id=id)
    dokumen.delete()
    return redirect("dokumen_integrasi")


def detail_dokumen_integrasi(request, id):
    dokumen = get_object_or_404(DokumenIntegrasi, id=id)
    return render(request, "backend/detailintegrasi.html", {"dokumen": dokumen})


# views.py
from django.core.cache import cache
from django.http import JsonResponse
import json

def get_allow_tambah_surat():
    return cache.get("allow_tambah_surat", True)  # default True

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def toggle_tambah_surat(request):
    if request.method == "POST" and request.user.is_superuser:
        data = json.loads(request.body)
        pengaturan, _ = Pengaturan.objects.get_or_create(id=1)
        pengaturan.allow_tambah_surat = data.get("allow", False)
        pengaturan.save()
        return JsonResponse({"success": True, "allow": pengaturan.allow_tambah_surat})
    return JsonResponse({"success": False}, status=400)

