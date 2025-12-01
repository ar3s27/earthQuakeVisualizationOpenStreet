import branca
from flask import Flask, render_template
import requests
import folium


app = Flask(__name__)

def fetch_earthquake_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Deprem Verileri Alınamadı:", response.status_code)
        return None

def get_marker_color(magnitude):
    if magnitude < 3.0:
        return '#2ecc71' # Green
    elif magnitude < 4.5:
        return '#f39c12' # Orange
    else:
        return '#e74c3c' # Red

def create_map_with_markers(data):
    # Haritayı başlatır - Modern tiles
    harita = folium.Map(location=[38.3335, 35.1500], zoom_start=6, tiles='CartoDB positron')
    
    # En güncel deprem verilerini alır
    most_recent_quake = None
    most_recent_date = ""
    for quake_id, entry in data.items():
        date = entry['date']
        if date > most_recent_date:
            most_recent_date = date
            most_recent_quake = entry

    # Circle'ın enlem ve boylamını en son depreme göre ayarla
    circle_latitude = most_recent_quake['latitude']
    circle_longitude = most_recent_quake['longitude']

    # Verideki her deprem olayı için işlem yapar
    for quake_id, entry in data.items():
        enlem = float(entry['latitude'])
        boylam = float(entry['longitude'])
        buyukluk = float(entry['magnitude'])
        derinlik = float(entry['depth'])
        lokasyon = entry['location']
        tarih = entry['date']

        # Pencere içeriğini oluşturur - Modern styling
        html = f"""
        <div style="font-family: 'Inter', sans-serif; font-size: 14px; color: #333;">
            <h4 style="margin: 0 0 8px 0; color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 4px;">{lokasyon}</h4>
            <div style="margin-bottom: 4px;"><strong>Büyüklük:</strong> <span style="background: {get_marker_color(buyukluk)}; color: white; padding: 2px 6px; border-radius: 4px;">{buyukluk}</span></div>
            <div style="margin-bottom: 4px;"><strong>Tarih:</strong> {tarih}</div>
            <div style="margin-bottom: 4px;"><strong>Derinlik:</strong> {derinlik} km</div>
            <div><strong>Enlem/Boylam:</strong> {enlem}, {boylam}</div>
        </div>
        """

        marker_color = get_marker_color(buyukluk)
        
        iframe = branca.element.IFrame(html=html, width=280, height=160)
        popup = folium.Popup(iframe, max_width=500)
        
        # Haritaya CircleMarker ekler
        is_most_recent = (entry == most_recent_quake)
        
        if is_most_recent:
             folium.Marker(
                location=[enlem, boylam],
                icon=folium.DivIcon(html=f"""<div class="pulsating-circle"></div>""")
            ).add_to(harita)

        folium.CircleMarker(
            location=[enlem, boylam],
            radius=buyukluk * 3, # Büyüklüğe göre yarıçap
            popup=popup,
            tooltip="En Son Deprem" if is_most_recent else None,
            color='black' if is_most_recent else marker_color,
            weight=3 if is_most_recent else 1,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.9 if is_most_recent else 0.7,
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

        # Deprem verilerini listeye çevir ve tarihe göre sırala (en yeni en üstte)
        earthquake_list = []
        for quake_id, entry in earthquake_data.items():
            earthquake_list.append(entry)
        
        # Tarihe göre sıralama (varsayılan format YYYY.MM.DD HH:MM:SS olduğu varsayılıyor)
        earthquake_list.sort(key=lambda x: x['date'], reverse=True)

        return render_template('index.html', map_html=map_html, earthquake_list=earthquake_list)
    else:
        return "Deprem verileri alınamadı."

if __name__ == '__main__':
    app.run(debug=True)
