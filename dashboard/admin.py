from django.contrib import admin
from .models import *

# Register your models here.



class PengikutInline(admin.TabularInline):  # bisa juga StackedInline kalau mau lebih panjang
    model = Pengikut
    extra = 1  # jumlah form kosong default yang muncul
    fields = ("nama", "nik", "kategori")  # field yang ditampilkan di inline

@admin.register(SuketRekKelTani)
class SuketRekKelTaniAdmin(admin.ModelAdmin):
    list_display = ("nama", "namawbp", "tanggal_kunjungan", "jenis_kunjungan", "status", "total_pengikut")
    list_filter = ("status", "jenis_kunjungan", "tanggal_kunjungan")
    search_fields = ("nama", "ktp", "namawbp", "hubungan")
    inlines = [PengikutInline]  # tampilkan pengikut langsung di bawah form Suket
    readonly_fields = ("date",)

@admin.register(Pengikut)
class PengikutAdmin(admin.ModelAdmin):
    list_display = ("nama", "nik", "kategori", "suket")
    list_filter = ("kategori",)
    search_fields = ("nama", "nik")


class AdPengumuman(admin.ModelAdmin):
    list_display = ["penulis", "judul", "konten", "date", "picture"]
admin.site.register(Pengumuman, AdPengumuman)

class AdBlog(admin.ModelAdmin):
    list_display = ["penulis", "judul", "konten", "date", "picture"]
admin.site.register(Blog, AdBlog)

class AdProfile(admin.ModelAdmin):
    list_display = ["user", "nik", "ktp"]
admin.site.register(Profile, AdProfile)

class AdPengaduanAsing(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "message","ktp"]
    search_fields = ["name", "email", "phone"]

admin.site.register(PengaduanAsing, AdPengaduanAsing)


class AdPengaduanAsingArsip(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "message", "ktp", "tanggal_arsip"]
    search_fields = ["name", "email", "phone"]
    readonly_fields = ["tanggal_arsip"]

admin.site.register(PengaduanAsingArsip, AdPengaduanAsingArsip)

from django.contrib import admin
from .models import IjinLuarBiasa

class AdIjinLuarBiasa(admin.ModelAdmin):
    list_display = [
        "nama_pengaju",
        "ktp_pengaju",
        "hubungan",
        "nama_wbp",
        "register_wbp",
        "alasan",
        "tanggal_ijin",
        "durasi",
        "tanggal_pengajuan",
        "status",
    ]
    search_fields = [
        "nama_pengaju",
        "ktp_pengaju",
        "nama_wbp",
        "register_wbp",
        "alasan",
    ]
    list_filter = ["status", "tanggal_pengajuan", "tanggal_ijin"]
    readonly_fields = ["tanggal_pengajuan"]

admin.site.register(IjinLuarBiasa, AdIjinLuarBiasa)




class BantuanHukumAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nama_pengaju",
        "ktp_pengaju",
        "alamat_pengaju",
        "hubungan",
        "nama_wbp",
        "tanggal_pengajuan",
        "status",
        "catatan_admin",
    )
    list_filter = ("status", "tanggal_pengajuan")
    search_fields = ("nama_pengaju", "nama_wbp", "ktp_pengaju")
    readonly_fields = ("tanggal_pengajuan",)

    fieldsets = (
        ("Data Pengaju", {
            "fields": ("nama_pengaju", "ktp_pengaju", "alamat_pengaju", "hubungan")
        }),
        ("Data WBP", {
            "fields": ("nama_wbp",)
        }),
        ("Dokumen Pendukung", {
            "fields": ("dokumen_ktp_kk", "dokumen_pernyataan", "dokumen_keterangan_desa")
        }),
        ("Status Pengajuan", {
            "fields": ("status", "catatan_admin", "tanggal_pengajuan")
        }),
    )

admin.site.register(BantuanHukum, BantuanHukumAdmin)


class DokumenIntegrasiAdmin(admin.ModelAdmin):
    list_display = ("judul", "tanggal_upload")
    search_fields = ("judul", "deskripsi")
    list_filter = ("tanggal_upload",)
    
admin.site.register(DokumenIntegrasi, DokumenIntegrasiAdmin)




