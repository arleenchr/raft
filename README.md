# Tugas Besar IF3230 Sistem Paralel dan Terdistribusi

## Deskripsi Program

Tugas Besar ini adalah implementasi dari algoritma Raft untuk konsensus terdistribusi, yang memastikan konsistensi data di antara beberapa server dalam sebuah cluster. Program ini terdiri dari server backend yang mengelola leader election, log replication, dan membership change, serta sebuah client web yang menyediakan interface untuk berinteraksi dengan sistem.

## Implementasi Raft

Raft adalah protokol konsensus yang digunakan untuk mengelola replika log dalam sistem terdistribusi. Implementasi ini mencakup empat komponen utama: 

### a. Membership Change

Membership Change dalam cluster Raft melibatkan penambahan atau penghapusan node dari cluster. Berikut adalah langkah-langkah yang diambil dalam implementasi ini:

1. Node yang ingin bergabung akan menghubungi node lain di dalam cluster menggunakan alamat kontak yang disediakan. Node tersebut akan mencoba untuk bergabung dengan cluster dengan mengirim request membership (`apply_membership`).

2. Jika node yang menerima request adalah leader, maka leader tersebut akan menambahkan node baru ke dalam daftar alamat cluster (`cluster_addr_list`) dan mengirimkan informasi membership baru kepada semua node dalam cluster (`__send_new_member_information`).

3. Semua node yang sudah ada dalam cluster akan diberitahu tentang member baru melalui panggilan RPC (`inform_new_member`).

4. Setiap node memperbarui daftar alamat cluster mereka untuk mencerminkan perubahan terbaru dalam membership cluster.

### b. Log Replication

Replikasi log adalah proses di mana leader memastikan bahwa semua entri log diterapkan pada semua node dalam cluster. Berikut adalah langkah-langkah dalam proses ini:

1. Ketika leader menerima request dari klien, request tersebut dicatat dalam log leader.

2. Leader mengirimkan entri log baru ke semua follower melalui RPC AppendEntries (`send_append_entries`).

3. Follower merespons dengan pengakuan (acknowledgement) jika mereka berhasil menambahkan entri log ke log mereka sendiri (`append_entries`).

4. Jika leader menerima pengakuan dari mayoritas node, leader akan menganggap entri log tersebut telah di-commit dan akan menerapkan perubahan yang diinginkan.

### c. Heartbeat

Heartbeat adalah sinyal periodik yang dikirim oleh leader ke semua follower untuk menunjukkan bahwa leader masih hidup dan untuk mencegah pemilihan leader baru. Berikut adalah proses pengiriman heartbeat:

1. Leader mengirim heartbeat ke semua follower pada interval tertentu (`__leader_heartbeat`).

2. Ketika follower menerima heartbeat (`heartbeat`), mereka mengatur ulang timer pemilihan mereka untuk mencegah pemilihan leader baru.

3. Dengan menerima heartbeat secara terus-menerus, follower mengetahui bahwa leader saat ini masih aktif dan bertanggung jawab atas cluster.

### d. Leader Election

Pemilihan leader terjadi ketika follower tidak menerima heartbeat dalam waktu yang ditentukan, atau ketika follower menerima term yang lebih tinggi dari leader saat ini. Berikut adalah langkah-langkah dalam pemilihan leader:

1. Ketika timer pemilihan habis, follower akan mengubah status menjadi kandidat dan memulai pemilihan baru dengan meningkatkan term saat ini dan memberikan suara untuk dirinya sendiri (`start_election`).

2. Kandidat mengirim request suara (`request_vote`) ke semua node dalam cluster.

3. Node yang menerima request suara akan memeriksa term dan log terbaru mereka, dan jika syaratnya terpenuhi, mereka akan memberikan suara kepada kandidat tersebut (`request_vote`).

4. Jika kandidat menerima suara dari mayoritas node dalam cluster, kandidat tersebut akan menjadi leader baru dan mulai mengirimkan heartbeat untuk mempertahankan statusnya sebagai leader (`__initialize_as_leader`).

## Fitur Tambahan

### a. Unit Test
Unit test digunakan untuk memastikan bahwa setiap komponen program bekerja dengan benar. Test ini mencakup berbagai fungsi dan modul dalam proyek, dan diimplementasikan menggunakan library unittest. Unit test membantu mendeteksi dan memperbaiki bug sebelum kode di-deploy.

### b. Web Client
Web client menyediakan interface pengguna yang intuitif untuk berinteraksi dengan sistem Raft. Pengguna dapat mengirim perintah, melihat status cluster, dan memantau log entri melalui halaman web. Web client ini dibangun menggunakan HTML dan JavaScript.

### c. Dashboard
Dashboard adalah fitur yang menyediakan visualisasi status cluster, termasuk leader saat ini, follower, dan log entri. Dashboard membantu dalam memantau dan mendiagnosis masalah dalam sistem dengan mudah. 

## Cara Menjalankan Program

### a. Server

Untuk menjalankan server, ikuti langkah-langkah berikut:

1. Pindah ke direktori `src`.
2. Install dependencies dengan menjalankan:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server dengan perintah:
   ```bash
   python server.py
   ```

### b. Client

Untuk menjalankan client, ikuti langkah-langkah berikut:

1. Pastikan server sudah berjalan.
2. Buka file `index.html` di browser Anda untuk mengakses antarmuka web client.

## Identitas


| Nama                              | NIM         |
|-----------------------------------|-------------|
| Kevin John Wesley Hutabarat       | 13521042    |
| Manuella Ivana Uli Sianipar       | 13521051    |
| Arleen Chrysantha Gunardi         | 13521059    |
| Muhammad Fadhil Amri              | 13521066    |
| Yobel Dean Christopher            | 13521067    |