import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SuketRekKelTani(models.Model):
    STATUS_CHOICES = [
        ('review', 'Proses Review'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]

    penulis = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    # Data pengunjung
    nama = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    telepon = models.CharField(max_length=255, blank=True, null=True)
    ktp = models.CharField(max_length=100)
    ttl = models.CharField(max_length=100)
    alamat = models.TextField()
    namawbp = models.CharField(max_length=255)
    hubungan = models.CharField(max_length=100)

    # Data kunjungan
    tanggal_kunjungan = models.DateField()
    jam_kunjungan = models.TimeField()
    jenis_kunjungan = models.CharField(max_length=100)

    # Jumlah pengikut berdasarkan kategori
    pengikut_laki = models.IntegerField(default=0)
    pengikut_perempuan = models.IntegerField(default=0)
    pengikut_anak = models.IntegerField(default=0)

    catatan_admin = models.TextField(blank=True, null=True)

    # Barang bawaan → TextField simpan JSON string biar aman di MySQL
    barang_bawaan = models.TextField(default="[]", blank=True)

    # Sistem
    date = models.DateTimeField(default=timezone.now, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='review')

    def __str__(self):
        return f"{self.nama} - {self.tanggal_kunjungan}"

    @property
    def total_pengikut(self):
        return self.pengikut_laki + self.pengikut_perempuan + self.pengikut_anak

    # Helper untuk ambil data barang_bawaan sebagai Python list
    def get_barang_bawaan(self):
        try:
            return json.loads(self.barang_bawaan)
        except Exception:
            return []

    # Helper untuk simpan data barang_bawaan dari Python list/dict
    def set_barang_bawaan(self, data):
        try:
            self.barang_bawaan = json.dumps(data, ensure_ascii=False)
        except Exception:
            self.barang_bawaan = "[]"

class Pengikut(models.Model):
    suket = models.ForeignKey(SuketRekKelTani, on_delete=models.CASCADE, related_name="pengikut")
    nama = models.CharField(max_length=255)
    nik = models.CharField(max_length=50, blank=True, null=True)
    kategori = models.CharField(
        max_length=20,
        choices=[('laki', 'Laki-laki'), ('perempuan', 'Perempuan'), ('anak', 'Anak-anak')]
    )

    def __str__(self):
        return f"{self.nama} ({self.kategori})"

    
class Pengumuman(models.Model):
    penulis = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    judul = models.CharField(max_length=200) 
    konten = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    picture = models.URLField(blank=True, null=True)
    
    def __str__(self):
      return "{} - {}".format(self.judul, self.konten)
    

class BeritaKetahananPangan(models.Model):
    penulis = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    judul = models.CharField(max_length=200) 
    isi = models.TextField()
    tanggal = models.DateTimeField(auto_now_add=True)
    gambar = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.judul} - {self.isi[:50]}"

class Blog(models.Model):
    penulis = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    judul = models.CharField(max_length=200) 
    konten = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    picture = models.URLField(blank=True, null=True)
    
    def __str__(self):
      return "{} - {}".format(self.judul, self.konten)
  
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nik = models.CharField(max_length=200)
    ktp = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

from django.db import models
from django.utils import timezone

class PengaduanAsing(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    ktp = models.URLField(blank=True, null=True)
    jawaban = models.TextField(blank=True, null=True)  # ← pastikan ini ada
    tanggal = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name or "Pengaduan Tanpa Nama"


class JawabanPengaduanAsing(models.Model):
    pengaduan = models.ForeignKey(
        PengaduanAsing,
        on_delete=models.CASCADE,
        related_name='jawaban_set'
    )
    jawaban = models.TextField()
    tanggal = models.DateTimeField(auto_now_add=True)
    dijawab_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)



class PengaduanAsingArsip(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    ktp = models.URLField(blank=True, null=True)
    tanggal_arsip = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.email)

class IjinLuarBiasa(models.Model):
    STATUS_CHOICES = [
        ('review', 'Proses Review'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    JENIS_IZIN_CHOICES = [
        ('menikah', 'Menikah'),
        ('wali_nikah', 'Wali Nikah'),
        ('sakit', 'Menjenguk Keluarga Sakit'),
        ('meninggal', 'Meninggal'),
        ('waris', 'Pembagian Waris'),
    ]

    # Data Pengaju
    nama_pengaju = models.CharField(max_length=150)
    ktp_pengaju = models.CharField(max_length=50)
    alamat_pengaju = models.TextField()
    hubungan = models.CharField(max_length=100)

    # Data WBP
    nama_wbp = models.CharField(max_length=150)
    register_wbp = models.CharField(max_length=50, blank=True, null=True)

    # Data Pengajuan
    jenis_izin = models.CharField(max_length=100, choices=JENIS_IZIN_CHOICES, null=True, blank=True)
    alasan = models.TextField()
    tanggal_ijin = models.DateField()
    durasi = models.IntegerField(help_text="Dalam hari")

    # Dokumen pendukung
    dokumen_ktp_kk = models.FileField(upload_to="ilb", blank=True, null=True)
    dokumen_pernyataan = models.FileField(upload_to="ilb", blank=True, null=True)
    dokumen_keterangan_desa = models.FileField(upload_to="ilb", blank=True, null=True)
    dokumen_sakit = models.FileField(upload_to="ilb", blank=True, null=True)         # 🔹 tambahan
    dokumen_kematian_rt = models.FileField(upload_to="ilb", blank=True, null=True)   # 🔹 tambahan
    dokumen_waris = models.FileField(upload_to="ilb", blank=True, null=True)         # 🔹 tambahan

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='review')
    catatan_admin = models.TextField(blank=True, null=True)

    # Tracking
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nama_wbp} - {self.nama_pengaju} ({self.status})"

class BantuanHukum(models.Model):
    STATUS_CHOICES = [
        ("pending", "Menunggu"),
        ("approved", "Disetujui"),
        ("rejected", "Ditolak"),
    ]

    # Data Pengaju
    penulis = models.ForeignKey(User, on_delete=models.CASCADE)  
    nama_pengaju = models.CharField(max_length=150)
    ktp_pengaju = models.CharField(max_length=50)  # bisa NIK/No KTP
    alamat_pengaju = models.TextField()
    hubungan = models.CharField(max_length=100)  # hubungan dengan WBP
    no_hp = models.CharField(max_length=20)
    pekerjaan_pengaju = models.CharField(max_length=100, blank=True, null=True)

    # Data WBP
    nama_wbp = models.CharField(max_length=150)
    blok_wbp = models.CharField(max_length=50, blank=True, null=True)  # opsional
    pasal = models.CharField(max_length=100, blank=True, null=True)
    lama_hukuman = models.CharField(max_length=100, blank=True, null=True)

    # Permasalahan Hukum
    kategori_permasalahan = models.CharField(
        max_length=50,
        choices=[
            ("pidana", "Pidana"),
            ("perdata", "Perdata"),
            ("narkotika", "Narkotika"),
            ("korupsi", "Korupsi"),
            ("lainnya", "Lainnya"),
        ]
    )
    kronologi = models.TextField()
    jenis_bantuan = models.CharField(max_length=200)  # simpan string (misal: "Pendampingan, Banding")

    # Dokumen Pendukung
    dokumen_ktp_kk = models.FileField(upload_to="bantuan_hukum/", blank=True, null=True)
    dokumen_surat_kuasa = models.FileField(upload_to="bantuan_hukum/", blank=True, null=True)
    dokumen_sktm = models.FileField(upload_to="bantuan_hukum/", blank=True, null=True)
    dokumen_putusan = models.FileField(upload_to="bantuan_hukum/", blank=True, null=True)
    dokumen_lainnya = models.FileField(upload_to="bantuan_hukum/", blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    catatan_admin = models.TextField(blank=True, null=True)
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama_pengaju} - {self.nama_wbp}"

class DokumenIntegrasi(models.Model): 
    
    judul = models.CharField(max_length=200) 
    deskripsi = models.TextField(blank=True, null=True) # opsional 
    file = models.FileField(upload_to="integrasi/") 
    tanggal_upload = models.DateTimeField(auto_now_add=True) 
    
    def __str__(self): return self.judul


class Pengaturan(models.Model):
    allow_tambah_surat = models.BooleanField(default=True)

    def __str__(self):
        return f"Tambah Surat: {'Aktif' if self.allow_tambah_surat else 'Nonaktif'}"
