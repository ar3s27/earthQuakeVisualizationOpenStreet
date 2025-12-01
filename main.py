import branca
from flask import Flask, render_template
import requests
import folium
import traceback

app = Flask(__name__)

def fetch_earthquake_data(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Deprem Verileri Alınamadı: {response.status_code}")
            return None
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None

def get_marker_color(magnitude):
    if magnitude < 3.0:
        return '#2ecc71' # Green
    elif magnitude < 4.0:
        return '#f1c40f' # Yellow
    elif magnitude < 5.0:
        return '#f39c12' # Orange
    elif magnitude < 6.0:
        return '#e67e22' # Dark Orange
    elif magnitude < 7.0:
        return '#d35400' # Red-Orange
    else:
        return '#c0392b' # Red

def create_map_with_markers(data):
    # Haritayı başlatır - Modern tiles
    harita = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')

    # En güncel deprem verilerini alır
    most_recent_quake = None
    most_recent_date = ""
    
    # Veri kontrolü
    if not data:
        return harita

    for quake_id, entry in data.items():
        try:
            date = entry.get('date', '')
            if date > most_recent_date:
                most_recent_date = date
                most_recent_quake = entry
        except Exception:
            continue

    # Verideki her deprem olayı için işlem yapar
    for quake_id, entry in data.items():
        try:
            enlem = float(entry['latitude'])
            boylam = float(entry['longitude'])
            buyukluk = float(entry['magnitude'])
            derinlik = float(entry['depth'])
            lokasyon = entry['location']
            tarih = entry['date']
        except (ValueError, KeyError, TypeError):
            continue

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
            radius=buyukluk * 6, # Büyüklüğe göre yarıçap
            popup=popup,
            tooltip="En Son Deprem" if is_most_recent else None,
            color='black' if is_most_recent else marker_color,
            weight=3 if is_most_recent else 1,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.9 if is_most_recent else 0.7,
        ).add_to(harita)

    return harita

@app.route('/map')
def map_page():
    try:
        # Deprem veri URL'si
        url = "https://deprem-gorsellestirme.vercel.app"
        # Deprem verilerini alır
        earthquake_data = fetch_earthquake_data(url)

        if earthquake_data:
            # İşaretli haritayı oluşturur
            map_with_markers = create_map_with_markers(earthquake_data)
            # Haritayı bir HTML dizesi olarak döndürür
            return map_with_markers._repr_html_()
        else:
            return "<h3>Harita yüklenemedi: Veri alınamadı.</h3>"
    except Exception as e:
        return f"<h3>Harita hatası: {str(e)}</h3><pre>{traceback.format_exc()}</pre>"

@app.route('/')
def index():
    try:
        # Deprem veri URL'si
        url = "https://deprem-gorsellestirme.vercel.app"

        # Deprem verilerini alır
        earthquake_data = fetch_earthquake_data(url)

        if earthquake_data:
            # Deprem verilerini listeye çevir ve tarihe göre sırala (en yeni en üstte)
            earthquake_list = []
            for quake_id, entry in earthquake_data.items():
                earthquake_list.append(entry)
            
            # Tarihe göre sıralama
            earthquake_list.sort(key=lambda x: x.get('date', ''), reverse=True)

            return render_template('index.html', earthquake_list=earthquake_list)
        else:
            return render_template('index.html', earthquake_list=[])
    except Exception as e:
        return f"Sayfa yükleme hatası: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
