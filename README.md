### Akademik Makale Öneri Sistemi

---

#### **Proje Açıklaması**
Bu proje, kullanıcıların akademik ilgi alanlarına ve okuma geçmişlerine göre kişiselleştirilmiş makale önerileri sunan bir web tabanlı sistemdir. Proje, kullanıcıların ilgilendiği makaleleri doğru bir şekilde önererek akademik çalışmalara katkı sağlamayı hedeflemektedir.

---

#### **Projenin Özellikleri**
- **Doğal Dil İşleme (NLP)**: Makalelerin işlenmesi ve kullanıcı profillerinin oluşturulması için NLP teknikleri kullanıldı.
- **Vektör Temsilleri**: **FastText** ve **SCIBERT** modelleri kullanılarak makaleler ve kullanıcı profilleri için vektör temsilleri oluşturuldu.
- **Benzerlik Hesaplama**: Kullanıcı-makale eşleştirmesi, **Cosine Similarity** metriği ile gerçekleştirildi.
- **Kişiselleştirilmiş Öneriler**: Kullanıcıların geçmişteki etkileşimlerine ve geri bildirimlerine göre dinamik olarak güncellenen öneriler sunuldu.
- **Geri Bildirim Sistemi**: Kullanıcılardan alınan geri bildirimler doğrultusunda öneri motoru sürekli optimize edildi.
- **Kullanıcı Dostu Arayüz**: Kullanıcıların kolayca sisteme kayıt olabileceği, profillerini yönetebileceği ve önerileri görüntüleyebileceği bir web arayüzü tasarlandı.

---

#### **Kullanılan Teknolojiler**
- **Python**: Projenin backend tarafı ve yapay zeka algoritmaları için.
- **NLP Kütüphaneleri**: 
  - **NLTK** veya **spaCy**: Metin işleme ve stopword temizliği.
  - **FastText** ve **SCIBERT**: Vektör temsilleri ve modelleme.
- **Flask**: Web arayüzü geliştirmek için.
- **HTML, CSS, JavaScript**: Kullanıcı dostu bir frontend oluşturmak için.
- **Cosine Similarity**: Kullanıcı profilleri ve makaleler arasındaki benzerlikleri ölçmek için.
- **MongoDB veya SQLite**: Kullanıcı verileri ve makale bilgilerini saklamak için.

---

#### **Proje Yapısı**
- **Backend**:
  - NLP tabanlı metin işleme, vektör temsilleri oluşturma ve öneri algoritmaları.
- **Frontend**:
  - Kullanıcı kayıt/giriş arayüzü, öneriler listesi, geri bildirim formları.
- **Veritabanı**:
  - Kullanıcı bilgileri, makale verileri ve kullanıcı etkileşimlerinin saklanması.

---

#### **Geliştirici**
Bu proje, yapay zeka, doğal dil işleme ve web geliştirme alanlarındaki bilgi ve deneyimimi kullanarak tamamen tarafımdan geliştirilmiştir. Projede hem **frontend** hem de **backend** süreçlerinden sorumluydum.

---

