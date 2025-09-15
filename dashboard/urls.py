from django.contrib import admin
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path("",dashboard, name="dashboard"),
    path("Pendaftaran-online/",suketrekkeltani,  name="suketrekkeltani"),
    path("Edit-pendaftaran/edit/<int:id>",edit_suketrekkeltani,  name="edit_suketrekkeltani"),
    path('Setujui-Pendaftaran/setujui/<int:id>/', setujui_suketrekeltani, name='setujui_suketrekeltani'),
    path('Tolak-Pendaftaran/tolak/<int:id>/', tolak_suketrekeltani, name='tolak_suketrekeltani'),
    path("Hapus-Pendaftaran/delete/<int:id>",delete_suketrekkeltani,  name="delete_suketrekkeltani"),
    path("Cetak-Pendaftaran/print/<int:id>",print_suketrekkeltani,  name="print_suketrekkeltani"),
    path("Detail-Pendaftar/detail/<int:id>", detail_suketrekkeltani, name="detail_suketrekkeltani"),
    path("tambah-pengumuman/", pengumuman, name="pengumuman"),
    path("tambah-pengumuman/edit/<int:id>", edit_pengumuman, name="edit_pengumuman"),
    path("tambah-pengumuman/delete/<int:id>", delete_pengumuman, name="delete_pengumuman"),
    path("tambah-blog/", blog, name="blog"),
    path("tambah-blog/edit/<int:id>", edit_blog, name="edit_blog"),
    path("tambah-blog/delete/<int:id>", delete_blog, name="delete_blog"),
    path("logout/", logoutPage, name="logout"),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('daftar-user/', daftaruser, name='daftar_user'),
    path('daftar-user/edit/<int:id>', edituser, name='edit_user'),
    path('daftar-user/delete/<int:id>', hapususers, name='hapus_user'),
    path('daftar-user/detail/<int:id>', detailuser, name='detail_user'),
    path('pengaduan-asing/', datapengaduanasing, name='pengaduan_asing'),
    path('pengaduan-asing/detail/<int:id>', detailpengaduanasing, name='detail_pengaduan_asing'),
    path('pengaduan-asing/delete/<int:id>', deletepengaduanasing, name='delete_pengaduan_asing'),
    path('pengaduan-asing/arsip/<int:id>/', views.arsip_pengaduan_asing, name='arsip_pengaduan_asing'),
    path('pengaduan-asing/arsip/', views.daftar_arsip_pengaduan_asing, name='daftar_arsip_pengaduan_asing'),
    path('pengaduan-asing/arsipkan/<int:id>/', views.arsip_pengaduan_asing, name='arsip_pengaduan_asing'),
    path('pengaduan-asing/arsip/detail/<int:id>/', views.detail_arsip_pengaduan_asing, name='detail_arsip_pengaduan_asing'),
    path('pengaduan-asing/arsip/', views.daftar_arsip_pengaduan_asing, name='arsip_pengaduan_asing'),
    path('pengaduan/partial/', views.pengaduan_partial, name='pengaduan_partial'),
    path("Ijin-Luar-Biasa/", ijinluarbiasa, name="ijinluarbiasa"),
    path("Edit-Ijin-Luar-Biasa/<int:id>/", edit_ilb, name="edit_ilb"),
    path("Setujui-Ijin-Luar-Biasa/<int:id>/", setujui_ilb, name="setujui_ilb"),
    path("Tolak-Ijin-Luar-Biasa/<int:id>/", tolak_ilb, name="tolak_ilb"),
    path("Hapus-Ijin-Luar-Biasa/<int:id>/", delete_ilb, name="delete_ilb"),
    path("detail-ILB/<int:id>/", detaililb, name="detail_ilb"),
    path("Cetak-Ijin-Luar-Biasa/<int:id>/", print_ilb, name="print_ilb"),
    path("bantuan-hukum/", views.bantuan_hukum, name="bantuan_hukum"),
    path("bantuan-hukum/<int:id>/", views.detail_bantuan_hukum, name="detail_bantuan_hukum"),
    path("bantuan-hukum/edit/<int:id>/", views.edit_bantuan_hukum, name="edit_bantuan_hukum"),
    path("bantuan-hukum/delete/<int:id>/", views.delete_bantuan_hukum, name="delete_bantuan_hukum"),
    path("bantuan-hukum/setuju/<int:id>/", views.setuju_bantuan_hukum, name="setuju_bantuan_hukum"),
    path("bantuan-hukum/tolak/<int:id>/", views.tolak_bantuan_hukum, name="tolak_bantuan_hukum"),
    path("dokumen-integrasi/", dokumen_integrasi, name="dokumen_integrasi"),
    path("dokumen-integrasi/detail/<int:id>/", detail_dokumen_integrasi, name="detail_dokumen_integrasi"),
    path("dokumen-integrasi/edit/<int:id>/", edit_dokumen_integrasi, name="edit_dokumen_integrasi"),
    path("dokumen-integrasi/delete/<int:id>/", delete_dokumen_integrasi, name="delete_dokumen_integrasi"),
    path("toggle-tambah-surat/", views.toggle_tambah_surat, name="toggle_tambah_surat"),
    path("tambah-ketahananpangan/", berita_ketahanan_pangan, name="berita_ketahanan_pangan"),
    path("tambah-ketahananpangan/edit/<int:id>", edit_berita_ketahanan_pangan, name="edit_berita_ketahanan_pangan"),
    path("tambah-ketahananpangan/delete/<int:id>", delete_berita_ketahanan_pangan, name="delete_berita_ketahanan_pangan"),





    path('register-admin/', register_super_admin, name='register_super_admin'),
    
    
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)