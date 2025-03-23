from flask import Flask, render_template_string
import numpy as np
from sklearn.linear_model import LinearRegression
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Mock historical data for AI modeling
historical_data = {
    'dates': ['2025-03-01', '2025-03-02', '2025-03-03', '2025-03-04', '2025-03-05'],
    'rainfall': [5, 10, 0, 15, 3],  # mm
    'soil_moisture': [60, 65, 55, 70, 62],  # %
    'temp': [25, 26, 24, 27, 25],  # °C
    'crop_health': [80, 85, 75, 90, 82]  # % health
}

# AI model to predict crop health
def predict_optimal_conditions(rainfall, moisture, temp):
    X = np.array([historical_data['rainfall'], historical_data['soil_moisture'], historical_data['temp']]).T
    y = historical_data['crop_health']
    model = LinearRegression()
    model.fit(X, y)
    prediction = model.predict([[rainfall, moisture, temp]])[0]
    return max(0, min(100, prediction))

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farm Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 30px;
            background-color: #e8ecef;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
        }
        .section {
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .section:hover {
            transform: translateY(-5px);
        }
        .section h2 {
            margin: 0 0 15px;
            color: #34495e;
            font-size: 1.5em;
        }
        .section h3 {
            margin: 15px 0 10px;
            color: #34495e;
            font-size: 1.2em;
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            font-size: 0.95em;
        }
        .alert-high {
            background-color: #ffebee;
            color: #c0392b;
        }
        .alert-low {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        .alert img {
            max-width: 80px;
            height: auto;
        }
        .recommendation {
            margin-top: 15px;
            font-style: italic;
            color: #555;
            font-size: 1em;
        }
        #soil-health {
            grid-column: span 2;
        }
        #watering-system {
            grid-column: span 1;
        }
        #drone-section {
            grid-column: span 2;
        }
        #alerts, #recommendations {
            grid-column: span 1;
        }
        #ai-insights {
            grid-column: span 1;
        }
        canvas, video {
            max-width: 100%;
            border-radius: 5px;
        }
        .timeline {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        .timeline li {
            padding: 10px;
            color: #444;
            font-size: 0.95em;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #eee;
        }
        .timeline li:last-child {
            border-bottom: none;
        }
        .status-box {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            display: inline-block;
        }
        .rainy {
            background-color: #c0392b;
        }
        .dry {
            background-color: #2e7d32;
        }
        .sms {
            background-color: #f5f5f5;
            padding: 12px;
            margin-top: 15px;
            border-radius: 8px;
            font-size: 0.9em;
            color: #666;
        }
        .ai-insights p {
            margin: 10px 0;
            font-size: 0.95em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .ai-insights .label {
            font-weight: bold;
            color: #34495e;
            min-width: 120px;
        }
        .ai-insights .health-good { color: #2e7d32; }
        .ai-insights .health-warning { color: #c0392b; }
        .ai-insights .tip {
            font-style: italic;
            color: #555;
            font-size: 0.9em;
        }
        .soil-status {
            height: 25px;
            margin-top: 15px;
            border-radius: 5px;
            text-align: center;
            color: #fff;
            line-height: 25px;
            font-size: 0.9em;
        }
        .soil-good {
            background-color: #2e7d32;
        }
        .soil-bad {
            background-color: #c0392b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ 'Farm Dashboard' if lang == 'en' else 'Dashibodi ya Shamba' }}</h1>
        <div class="grid">
            <div class="section">
                <h2>{{ 'Weather Forecast' if lang == 'en' else 'Utabiri wa Hali ya Hewa' }}</h2>
                <canvas id="weatherChart"></canvas>
            </div>
            <div class="section" id="watering-system">
                <h2>{{ 'Watering System Forecast' if lang == 'en' else 'Utabiri wa Mfumo wa Kumwagilia' }}</h2>
                <canvas id="wateringChart"></canvas>
            </div>
            <div class="section" id="ai-insights">
                <h2>{{ 'AI Farming Insights' if lang == 'en' else 'Maarifa ya AI ya Kilimo' }}</h2>
                <p><span class="label">Crop Health:</span> <span class="{{ 'health-good' if crop_health_pred >= 70 else 'health-warning' }}">{{ crop_health_pred|round(1) }}%</span> (Confidence: {{ confidence }}%)</p>
                <p><span class="label">Status:</span> <span class="{{ 'health-good' if crop_health_pred >= 70 else 'health-warning' }}">{{ health_status }}</span></p>
                <p><span class="label">Optimal Conditions:</span> Rain {{ optimal_conditions.rain|round(1) }} mm, Moisture {{ optimal_conditions.moisture|round(1) }}%, Temp {{ optimal_conditions.temp|round(1) }}°C</p>
                <p><span class="label">Rotation Suggestion:</span> {{ 'Switch to legumes next season to improve soil nitrogen.' if lang == 'en' else 'Badilisha kwa jamii ya kunde msimu ujao ili kuboresha nitrojeni ya udongo.' }}</p>
                <p class="tip">{{ 'Maintain current irrigation levels.' if crop_health_pred >= 70 else 'Check soil nutrients and adjust irrigation.' }}</p>
            </div>
            <div class="section" id="soil-health">
                <h2>{{ 'Soil Health' if lang == 'en' else 'Afya ya Udongo' }}</h2>
                <canvas id="soilChart"></canvas>
                <div class="soil-status {{ 'soil-good' if soil_moisture >= 60 else 'soil-bad' }}">
                    {{ 'Good Condition' if soil_moisture >= 60 else 'Bad Condition' if lang == 'en' else 'Hali Nzuri' if soil_moisture >= 60 else 'Hali Mbaya' }}
                </div>
            </div>
            <div class="section" id="alerts">
                <h2>{{ 'Alerts' if lang == 'en' else 'Tahadhari' }}</h2>
                {% for alert in alerts %}
                    <p class="alert {{ 'alert-high' if alert.level == 'high' else 'alert-low' }}">
                        {% if alert.image %}
                            <img src="{{ alert.image }}" alt="{{ alert.message }}">
                        {% endif %}
                        {{ alert.message }} <small>({{ alert.timestamp }})</small>
                    </p>
                {% endfor %}
            </div>
            <div class="section" id="drone-section">
                <h2>{{ 'Drone Spray & Camera' if lang == 'en' else 'Droni ya Kunyunyizia & Kamera' }}</h2>
                <h3>{{ 'Pesticide Spray Schedule' if lang == 'en' else 'Ratiba ya Kunyunyizia Dawa' }}</h3>
                <ul class="timeline">
                    {% for event in spray_timeline %}
                        <li>
                            <span class="status-box {{ 'rainy' if event.rainy else 'dry' }}"></span>
                            {{ event.text }}
                        </li>
                    {% endfor %}
                </ul>
                <h3>{{ 'Drone Camera Feed' if lang == 'en' else 'Mlisho wa Kamera ya Droni' }}</h3>
                <video controls autoplay loop muted>
                    <source src="https://videos.pexels.com/video-files/2758322/2758322-uhd_2560_1440_30fps.mp4">
                    {{ 'Your browser does not support the video tag.' if lang == 'en' else 'Kivinjari chako hakitumii video.' }}
                </video>
            </div>
            <div class="section" id="recommendations">
                <h2>{{ 'Recommendations' if lang == 'en' else 'Mapendekezo' }}</h2>
                <p class="recommendation">{{ recommendation }}</p>
                <div class="sms">{{ 'SMS Alert' if lang == 'en' else 'Tahadhari ya SMS' }}: {{ recommendation }}</div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const weatherCtx = document.getElementById('weatherChart').getContext('2d');
            const soilCtx = document.getElementById('soilChart').getContext('2d');
            const wateringCtx = document.getElementById('wateringChart').getContext('2d');

            const weatherData = {{ weather_data|tojson }};
            new Chart(weatherCtx, {
                type: 'line',
                data: weatherData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: '{{ 'Next 5 Days' if lang == 'en' else 'Siku 5 Zijazo' }}' }
                    }
                }
            });

            const soilData = {{ soil_data|tojson }};
            new Chart(soilCtx, {
                type: 'bar',
                data: soilData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: '{{ 'Current Metrics' if lang == 'en' else 'Vipimo vya Sasa' }}' }
                    },
                    scales: { y: { beginAtZero: true } }
                }
            });

            const wateringData = {{ watering_data|tojson }};
            new Chart(wateringCtx, {
                type: 'line',
                data: wateringData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: '{{ 'Next 5 Days' if lang == 'en' else 'Siku 5 Zijazo' }}' }
                    }
                }
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    lang = 'en'  # Switch to 'sw' for Swahili

    # Random weather data with lower rain rate
    rainfall = [random.uniform(0, 5) for _ in range(5)]
    weather_data = {
        'labels': ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
        'datasets': [{
            'label': 'Rainfall (mm)',
            'data': rainfall,
            'borderColor': '#1e90ff',
            'backgroundColor': 'rgba(30, 144, 255, 0.1)',
            'fill': True,
            'tension': 0.3
        }]
    }
    total_rain = sum(rainfall)
    avg_temp = random.uniform(20, 30)

    # Watering system forecast
    watering_volumes = [max(0, 15 - rain) for rain in rainfall]
    watering_data = {
        'labels': ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
        'datasets': [{
            'label': 'Watering Volume (mm)',
            'data': watering_volumes,
            'borderColor': '#32cd32',
            'backgroundColor': 'rgba(50, 205, 50, 0.1)',
            'fill': True,
            'tension': 0.3
        }]
    }

    # Soil data
    soil_moisture = random.uniform(55, 75)
    soil_data = {
        'labels': ['Moisture (%)', 'pH', 'Nitrogen (mg/kg)'],
        'datasets': [{
            'label': 'Soil Metrics',
            'data': [soil_moisture, 6.2, 18],
            'backgroundColor': ['#32cd32', '#ffa500', '#8a2be2'],
            'borderColor': '#fff',
            'borderWidth': 1
        }]
    }

    # AI prediction
    crop_health_pred = predict_optimal_conditions(total_rain / 5, soil_moisture, avg_temp)
    confidence = 90  # Fixed at 90%
    health_status = "Good" if crop_health_pred >= 90 else "Warning - Action Needed"
    optimal_conditions = {'rain': 10, 'moisture': 65, 'temp': 25}

    # Alerts with images, timestamps, and soil condition
    now = datetime.now()
    alerts = [
        {'level': 'high', 'message': 'Pest outbreak likely in 3 days.', 'timestamp': now.strftime('%Y-%m-%d %I:%M %p')},
        {'level': 'low', 'message': 'Moisture levels optimal.', 'timestamp': (now - timedelta(minutes=30)).strftime('%Y-%m-%d %I:%M %p')},
        {'level': 'high', 'message': 'Drone detected potential snake near field edge.', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSs7ooPnj7HdV8aWicOFXQM6FTLtfdO6dxhiw&s', 'timestamp': (now - timedelta(hours=1)).strftime('%Y-%m-%d %I:%M %p')},
        {'level': 'high', 'message': 'Eagle spotted above farm - possible threat.', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRv224bC0r7NXpZIoDldeF36NH1yBh1wJAcnA&s', 'timestamp': (now - timedelta(hours=2)).strftime('%Y-%m-%d %I:%M %p')}
    ]
    if total_rain < 5:
        alerts.append({'level': 'high', 'message': 'Drought risk detected - low rainfall.', 'timestamp': now.strftime('%Y-%m-%d %I:%M %p')})
    if crop_health_pred < 70:
        alerts.append({'level': 'high', 'message': 'Crop health declining - check soil.', 'timestamp': now.strftime('%Y-%m-%d %I:%M %p')})
    if soil_moisture < 60:
        alerts.append({
            'level': 'high', 
            'message': f'Low soil moisture detected ({soil_moisture:.1f}%). Suggestion: Increase irrigation by 15 mm.', 
            'timestamp': now.strftime('%Y-%m-%d %I:%M %p')
        })

    # Recommendations
    recommendation = "Irrigate 10 mm tomorrow morning."
    if total_rain > 15:
        recommendation = "Stop watering - sufficient rain detected."
    if crop_health_pred < 70:
        recommendation += " Apply 5 kg/ha fertilizer to boost health."
    if total_rain > 20:
        recommendation += " Reduce pesticide use due to heavy rain."
    if soil_moisture < 60:
        recommendation += " Increase irrigation by 15 mm due to low soil moisture."

    # Dynamic pesticide spray schedule based on rainfall
    today = datetime.now()
    spray_timeline = []
    spray_count = 3
    day_offset = 0
    for i in range(5):
        if spray_count == 0:
            break
        rain = rainfall[i]
        date = today + timedelta(days=i + day_offset)
        rainy = rain > 2
        if not rainy:
            spray_timeline.append({
                'text': f"{date.strftime('%B %d, %Y')}: Scheduled spray at 6 PM",
                'rainy': False
            })
            spray_count -= 1
        else:
            spray_timeline.append({
                'text': f"{date.strftime('%B %d, %Y')}: Spray postponed due to rain ({rain:.1f} mm)",
                'rainy': True
            })
            day_offset += 1

    return render_template_string(
        HTML_TEMPLATE,
        weather_data=weather_data,
        soil_data=soil_data,
        watering_data=watering_data,
        spray_timeline=spray_timeline,
        alerts=alerts,
        recommendation=recommendation,
        lang=lang,
        crop_health_pred=crop_health_pred,
        confidence=confidence,
        health_status=health_status,
        optimal_conditions=optimal_conditions,
        soil_moisture=soil_moisture,
        total_rain=total_rain
    )

if __name__ == '__main__':
    app.run(debug=True)