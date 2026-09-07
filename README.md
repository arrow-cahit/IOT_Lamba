# IoT Lamba & Röle Kontrol Sistemi (ESP8266 & JSON Tabanlı)

Bu proje, harici bulut servislerine (Firebase vb.) ihtiyaç duymadan, yerel ağınızda doğrudan bir `data.json` dosyası üzerinden lamba ve röle durumlarını kontrol etmenizi sağlar.

## 📁 Proje Yapısı

- **`index.html`**: Modern, karanlık tema, gerçekçi lamba animasyonu ve canlı JSON izleyicisi içeren kontrol paneli.
- **`data.json`**: Lamba ve rölelerin açık/kapalı durumlarını saklayan veri dosyası.
- **`server.py`**: Ekstra kurulum (pip) gerektirmeyen, Python standart kütüphanesiyle çalışan HTTP sunucusu. Web arayüzünden gelen isteklerle `data.json` dosyasını günceller.
- **`baslat.bat`**: Sunucuyu tek tıklamayla başlatıp web panelini açan Windows başlatıcı.

---

## 🚀 Başlatma & Kullanım

1. `baslat.bat` dosyasına çift tıklayın (veya komut satırında `python server.py` çalıştırın).
2. Tarayıcınızda `http://localhost:8000` adresi açılacaktır.
3. Web panelindeki **"Lambayı Aç / Kapat"** veya röle butonlarına bastığınızda, aynı dizindeki `data.json` dosyasındaki ilgili değişken anlık olarak değişecek ve diske kaydedilecektir.

---

## 📶 ESP8266 / NodeMCU Bağlantısı

ESP8266 kartınız bilgisayarınızla aynı WiFi ağına bağlı olduğunda, lamba durumunu okumak için şu adrese `HTTP GET` isteği gönderebilir:

```text
http://<BILGISAYARINIZIN_YEREL_IP_ADRESI>:8000/data.json
```

### Örnek JSON Yanıtı:
```json
{
  "lamba": true,
  "relayA": true,
  "relayB": false,
  "durum": "ACIK",
  "son_guncelleme": "2026-09-07 21:10:00"
}
```

### Örnek ESP8266 Arduino Kodu (Özet):
```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";
const char* serverUrl = "http://192.168.1.50:8000/data.json"; // Sunucu IP'si

void setup() {
  pinMode(D1, OUTPUT); // Lamba Rölesi
  WiFi.begin(ssid, password);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, serverUrl);
    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      StaticJsonDocument<200> doc;
      deserializeJson(doc, payload);
      bool lambaDurumu = doc["lamba"];
      digitalWrite(D1, lambaDurumu ? HIGH : LOW);
    }
    http.end();
  }
  delay(1000); // 1 saniyede bir kontrol et
}
```
