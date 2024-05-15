import branca
from flask import Flask, render_template
import requests
import folium
from calculations import earthquake_percentage,earthquake_location

app = Flask(__name__)

def fetch_earthquake_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Deprem Verileri Alınamadı:", response.status_code)
        return None

def create_map_with_markers(data):
    # Haritayı başlatır
    harita = folium.Map(location=[38.3335, 35.1500], zoom_start=6)
    # En güncel deprem verilerini alır
    most_recent_quake = None
    most_recent_date = ""
    for quake_id, entry in data.items():
        date = entry['date']
        if date > most_recent_date:
            most_recent_date = date
            most_recent_quake = entry

    # Verideki her deprem olayı için işlem yapar
    for quake_id, entry in data.items():
        enlem = float(entry['latitude'])
        boylam = float(entry['longitude'])
        buyukluk = entry['magnitude']
        derinlik = entry['depth']
        lokasyon = entry['location']

        # Pencere içeriğini oluşturur
        html = f"""<h4>Lokasyon: {lokasyon}<br>
        Enlem: {enlem}<br>
        Boylam: {boylam}<br>
        Büyüklük: {buyukluk}<br>
        Derinlik: {derinlik}</h4>"""

        # En son depreme göre işaret rengini belirler
        if entry == most_recent_quake:
            marker_color = 'red'  #  En son deprem işareti için istediğiniz rengi seçebilirsiniz
        else:
            marker_color = 'blue'
        
        iframe = branca.element.IFrame(html=html, width=250, height=125)
        popup = folium.Popup(iframe, max_width=500)
        # Haritaya işaret ekler
        folium.Marker([enlem, boylam], popup=popup, icon=folium.Icon(color=marker_color)).add_to(harita)

    # Daire ekler
    circle = folium.Circle(
        location=earthquake_location(),
        radius=400000,
        color="red",
        fill=True,
        fill_color="red",
        tooltip=f"<h4>Bu Bölgede 3.5 Üzeri Deprem Olma Olasığı %{earthquake_percentage()}</h4>",
    ).add_to(harita)
    
    return harita

@app.route('/')
def index():
    # Deprem veri URL'si
    url = "https://deprem-gorsellestirme.vercel.app"

    # Deprem verilerini alır
    earthquake_data = fetch_earthquake_data(url)

    if earthquake_data:
        # İşaretli haritayı oluşturur
        map_with_markers = create_map_with_markers(earthquake_data)

        # Haritayı bir HTML dizesi olarak kaydeder
        map_html = map_with_markers._repr_html_()

        return render_template('index.html', map_html=map_html)
    else:
        return "Deprem verileri alınamadı."

if __name__ == '__main__':
    app.run(debug=True)
