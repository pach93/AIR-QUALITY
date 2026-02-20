#!/usr/bin/env python3
"""
Génère un PDF d'architecture Docker pour une application Spring Boot + MySQL.
Tutoriel Examen M2 UAHB - Architecture de dockerisation.

Usage: python generate_architecture.py
Produit: ARCHITECTURE_DOCKER.pdf
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ArrowStyle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import numpy as np
import requests
import os
import sys
from io import BytesIO

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
COLORS = {
    'docker':       '#2496ED',
    'docker_dark':  '#1D76C7',
    'mysql_orange': '#F29111',
    'mysql_blue':   '#00758F',
    'spring':       '#6DB33F',
    'spring_dark':  '#5A9A30',
    'swagger':      '#85EA2D',
    'java':         '#ED8B00',
    'java_red':     '#5382A1',
    'env_red':      '#C62828',
    'network_bg':   '#EBF5FB',
    'network_border': '#2496ED',
    'volume_bg':    '#FFF3E0',
    'section_bg':   '#FAFAFA',
    'white':        '#FFFFFF',
    'dark':         '#212121',
    'grey':         '#757575',
    'light_grey':   '#F5F5F5',
    'title_bg':     '#1A237E',
    'title_accent': '#3F51B5',
    'flow_bg':      '#F3E5F5',
    'dockerfile_bg':'#FFF8E1',
}

LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos')

LOGO_URLS = {
    'docker': [
        'https://www.pinclipart.com/picdir/big/174-1748630_a-blue-whale-with-containers-on-its-back.png',
    ],
    'mysql': [
        'https://toppng.com/uploads/preview/mysql-logo-png-image-11660514413jvwkcjh4av.png',
    ],
    'spring': [
        'https://raw.githubusercontent.com/spring-projects/spring-framework/main/framework-docs/src/docs/spring-framework.png',
    ],
    'swagger': [
        'https://pngate.com/wp-content/uploads/2025/05/swagger-api-logo-green-circle-braces-icon-flat-design-1.png',
    ],
    'java': [
        'https://wallpapers.com/images/hd/java-programming-language-logo-transparent-rbo1dxbpo1nnuvaa-2.png',
    ],
}

# ---------------------------------------------------------------------------
# Logo helpers
# ---------------------------------------------------------------------------
def download_logo(name, urls, dest_dir):
    path = os.path.join(dest_dir, f'{name}.png')
    if os.path.exists(path):
        try:
            img = Image.open(path)
            img.verify()
            return path
        except Exception:
            os.remove(path)

    os.makedirs(dest_dir, exist_ok=True)
    for url in urls:
        try:
            r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200 and len(r.content) > 500:
                with open(path, 'wb') as f:
                    f.write(r.content)
                Image.open(path).verify()
                return path
        except Exception:
            if os.path.exists(path):
                os.remove(path)
    return None


def load_logo(name, size=0.35):
    path = os.path.join(LOGO_DIR, f'{name}.png')
    if not os.path.exists(path):
        path = download_logo(name, LOGO_URLS.get(name, []), LOGO_DIR)
    if path is None:
        return None
    try:
        img = Image.open(path).convert('RGBA')
        w, h = img.size
        ratio = min(size * 300 / w, size * 300 / h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        return np.array(img)
    except Exception:
        return None


def place_logo(ax, name, xy, zoom=0.18):
    arr = load_logo(name, size=1.0)
    if arr is not None:
        im = OffsetImage(arr, zoom=zoom)
        im.image.axes = ax
        ab = AnnotationBbox(im, xy, frameon=False, zorder=10)
        ax.add_artist(ab)
        return True
    return False


def draw_placeholder(ax, xy, color, label, size=0.12):
    from matplotlib.patches import Circle
    c = Circle(xy, size, fc=color, ec='white', lw=2, zorder=10, alpha=0.85)
    ax.add_patch(c)
    ax.text(xy[0], xy[1], label, ha='center', va='center',
            fontsize=5.5, fontweight='bold', color='white', zorder=11)


def place_logo_or_placeholder(ax, name, xy, color, label, zoom=0.18):
    if not place_logo(ax, name, xy, zoom=zoom):
        draw_placeholder(ax, xy, color, label)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def rounded_box(ax, xy, width, height, color, alpha=1.0, lw=1.5, ec=None,
                zorder=2, fc=None, style='round,pad=0.02'):
    x, y = xy
    box = FancyBboxPatch((x, y), width, height, boxstyle=style,
                         fc=fc or color, ec=ec or color, lw=lw,
                         alpha=alpha, zorder=zorder)
    ax.add_patch(box)
    return box


def draw_arrow(ax, start, end, color='#455A64', lw=1.8, style='->', zorder=5,
               connectionstyle='arc3,rad=0'):
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle=style,
        color=color,
        lw=lw,
        zorder=zorder,
        connectionstyle=connectionstyle,
        mutation_scale=14,
    )
    ax.add_patch(arrow)


def section_title(ax, x, y, text, color, fontsize=11):
    ax.text(x, y, text, fontsize=fontsize, fontweight='bold', color=color,
            ha='left', va='center', zorder=15,
            fontfamily='sans-serif')


def label_text(ax, x, y, text, fontsize=7, color='#333333', ha='left',
               va='center', weight='normal', style_='normal', zorder=12):
    ax.text(x, y, text, fontsize=fontsize, color=color, ha=ha, va=va,
            fontweight=weight, fontstyle=style_, zorder=zorder,
            fontfamily='sans-serif')


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def generate_pdf():
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'ARCHITECTURE_DOCKER.pdf')

    fig = plt.figure(figsize=(8.27, 11.69), dpi=200)
    fig.patch.set_facecolor('#FDFDFD')

    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')

    # ======================================================================
    # HEADER / TITLE
    # ======================================================================
    rounded_box(ax, (0.2, 13.0), 9.6, 0.85, COLORS['title_bg'], ec=COLORS['title_bg'],
                lw=0, zorder=3, style='round,pad=0.03')
    rounded_box(ax, (0.2, 13.0), 9.6, 0.06, COLORS['docker'], ec=COLORS['docker'],
                lw=0, zorder=4, style='square,pad=0')

    ax.text(5.0, 13.55, 'Architecture Docker — Spring Boot + MySQL',
            fontsize=14, fontweight='bold', color='white', ha='center', va='center',
            zorder=15, fontfamily='sans-serif')
    ax.text(5.0, 13.18, 'Tutoriel Examen M2 UAHB  |  Diagramme d\'architecture de dockerisation',
            fontsize=7.5, color='#B0BEC5', ha='center', va='center',
            zorder=15, fontfamily='sans-serif')

    place_logo_or_placeholder(ax, 'docker', (1.0, 13.42), COLORS['docker'], 'Docker', zoom=0.08)

    # ======================================================================
    # SECTION 1: DOCKER COMPOSE ARCHITECTURE
    # ======================================================================
    sec1_y = 7.6
    sec1_h = 5.25
    rounded_box(ax, (0.3, sec1_y), 9.4, sec1_h, COLORS['section_bg'],
                ec='#E0E0E0', lw=1.2, zorder=1, style='round,pad=0.02')

    # Section title
    place_logo_or_placeholder(ax, 'docker', (0.9, sec1_y + sec1_h - 0.35),
                              COLORS['docker'], 'D', zoom=0.06)
    section_title(ax, 1.25, sec1_y + sec1_h - 0.35,
                  'DOCKER COMPOSE', COLORS['docker'], fontsize=10)
    label_text(ax, 3.65, sec1_y + sec1_h - 0.35,
               '(docker-compose.yml)', fontsize=7, color=COLORS['grey'], style_='italic')

    # --- .env box ---
    env_x, env_y = 0.6, 11.15
    rounded_box(ax, (env_x, env_y), 2.3, 0.95, '#FFEBEE',
                ec=COLORS['env_red'], lw=1.5, zorder=3, style='round,pad=0.02')
    rounded_box(ax, (env_x + 0.08, env_y + 0.63), 0.25, 0.22, COLORS['env_red'],
                ec='none', lw=0, zorder=4, style='round,pad=0.01', alpha=0.15)
    label_text(ax, env_x + 0.5, env_y + 0.73, '.env  (secrets)',
               fontsize=7.5, weight='bold', color=COLORS['env_red'])
    label_text(ax, env_x + 0.15, env_y + 0.48, 'MYSQL_ROOT_PASSWORD',
               fontsize=5.5, color='#555')
    label_text(ax, env_x + 0.15, env_y + 0.30, 'MYSQL_DATABASE',
               fontsize=5.5, color='#555')
    label_text(ax, env_x + 0.15, env_y + 0.12, 'SPRING_DATASOURCE_URL',
               fontsize=5.5, color='#555')

    # --- Variables Env box ---
    var_x, var_y = 3.5, 11.15
    rounded_box(ax, (var_x, var_y), 3.2, 0.95, '#E3F2FD',
                ec=COLORS['docker'], lw=1.2, zorder=3, style='round,pad=0.02')
    label_text(ax, var_x + 0.15, var_y + 0.73, 'Variables d\'environnement',
               fontsize=7, weight='bold', color=COLORS['docker_dark'])
    envs = [
        'MYSQL_ROOT_PASSWORD=${...}',
        'SPRING_DATASOURCE_URL=jdbc:mysql://...',
        'SPRING_DATASOURCE_USERNAME=root',
    ]
    for i, e in enumerate(envs):
        label_text(ax, var_x + 0.15, var_y + 0.48 - i * 0.18, e,
                   fontsize=5, color='#455A64', style_='normal')

    # Arrow .env -> variables
    draw_arrow(ax, (env_x + 2.3, env_y + 0.47), (var_x, var_y + 0.47),
               color=COLORS['env_red'], lw=1.5, style='->')

    # ======================================================================
    # NETWORK BOX
    # ======================================================================
    net_x, net_y = 0.6, 8.0
    net_w, net_h = 8.8, 3.35
    rounded_box(ax, (net_x, net_y), net_w, net_h, COLORS['network_bg'],
                ec=COLORS['network_border'], lw=2, zorder=2,
                style='round,pad=0.03', alpha=0.6)
    label_text(ax, net_x + 0.2, net_y + net_h - 0.22,
               'docker-demo-network  (bridge)', fontsize=7,
               weight='bold', color=COLORS['docker_dark'])
    # small network icon
    circle_net = plt.Circle((net_x + net_w - 0.45, net_y + net_h - 0.22), 0.12,
                             fc=COLORS['docker'], ec='white', lw=1, zorder=5, alpha=0.3)
    ax.add_patch(circle_net)

    # --- MYSQL Container ---
    mysql_x, mysql_y = 1.0, 8.25
    mysql_w, mysql_h = 3.6, 2.75
    rounded_box(ax, (mysql_x, mysql_y), mysql_w, mysql_h, COLORS['white'],
                ec=COLORS['mysql_blue'], lw=2, zorder=3, style='round,pad=0.02')

    # MySQL logo
    place_logo_or_placeholder(ax, 'mysql', (mysql_x + 0.45, mysql_y + mysql_h - 0.35),
                              COLORS['mysql_blue'], 'MySQL', zoom=0.06)
    label_text(ax, mysql_x + 0.85, mysql_y + mysql_h - 0.35,
               'MySQL 8.0', fontsize=8.5, weight='bold', color=COLORS['mysql_blue'])

    # port badge
    rounded_box(ax, (mysql_x + 2.4, mysql_y + mysql_h - 0.52), 1.0, 0.3,
                COLORS['mysql_orange'], ec=COLORS['mysql_orange'], lw=0, zorder=4,
                alpha=0.2, style='round,pad=0.01')
    label_text(ax, mysql_x + 2.9, mysql_y + mysql_h - 0.37,
               'Port: 3307', fontsize=6, weight='bold', color=COLORS['mysql_orange'], ha='center')

    # MySQL details
    mysql_details = [
        ('Container:', 'docker-mysql'),
        ('Image:', 'mysql:8.0'),
        ('Volume:', 'mysql_data:/var/lib/mysql'),
        ('', ''),
        ('Healthcheck:', ''),
        ('  cmd:', 'mysqladmin ping -h localhost'),
        ('  interval:', '10s / timeout: 5s'),
        ('  retries:', '5'),
    ]
    y_off = mysql_y + mysql_h - 0.75
    for key, val in mysql_details:
        if key == '' and val == '':
            y_off -= 0.08
            continue
        label_text(ax, mysql_x + 0.2, y_off, key, fontsize=5.2,
                   weight='bold', color='#455A64')
        label_text(ax, mysql_x + 0.2 + len(key) * 0.05 + 0.08, y_off, val,
                   fontsize=5.2, color='#666')
        y_off -= 0.2

    # --- SPRING BOOT Container ---
    spring_x, spring_y = 5.4, 8.25
    spring_w, spring_h = 3.6, 2.75
    rounded_box(ax, (spring_x, spring_y), spring_w, spring_h, COLORS['white'],
                ec=COLORS['spring'], lw=2, zorder=3, style='round,pad=0.02')

    place_logo_or_placeholder(ax, 'spring', (spring_x + 0.4, spring_y + spring_h - 0.35),
                              COLORS['spring'], 'Spring', zoom=0.12)
    label_text(ax, spring_x + 0.75, spring_y + spring_h - 0.35,
               'Spring Boot App', fontsize=8.5, weight='bold', color=COLORS['spring_dark'])

    # port badge
    rounded_box(ax, (spring_x + 2.4, spring_y + spring_h - 0.52), 1.0, 0.3,
                COLORS['spring'], ec=COLORS['spring'], lw=0, zorder=4,
                alpha=0.2, style='round,pad=0.01')
    label_text(ax, spring_x + 2.9, spring_y + spring_h - 0.37,
               'Port: 8080', fontsize=6, weight='bold', color=COLORS['spring_dark'], ha='center')

    spring_details = [
        ('Container:', 'docker-spring-boot'),
        ('Build:', './  (Dockerfile multi-stage)'),
        ('depends_on:', 'mysql (condition: healthy)'),
        ('', ''),
        ('Endpoints:', ''),
        ('  API:', '/api/users'),
        ('  Health:', '/actuator/health'),
        ('  Swagger:', '/swagger-ui.html'),
    ]
    y_off = spring_y + spring_h - 0.75
    for key, val in spring_details:
        if key == '' and val == '':
            y_off -= 0.08
            continue
        label_text(ax, spring_x + 0.2, y_off, key, fontsize=5.2,
                   weight='bold', color='#455A64')
        label_text(ax, spring_x + 0.2 + len(key) * 0.05 + 0.08, y_off, val,
                   fontsize=5.2, color='#666')
        y_off -= 0.2

    # Arrow Spring -> MySQL (connection)
    arrow_start = (spring_x, spring_y + spring_h / 2)
    arrow_end = (mysql_x + mysql_w, mysql_y + mysql_h / 2)
    draw_arrow(ax, arrow_start, arrow_end, color=COLORS['spring_dark'], lw=2.2,
               style='->', connectionstyle='arc3,rad=0')
    label_text(ax, (arrow_start[0] + arrow_end[0]) / 2, spring_y + spring_h / 2 + 0.18,
               'JDBC / TCP 3306', fontsize=5.5, ha='center', weight='bold',
               color=COLORS['mysql_blue'])

    # --- VOLUME box ---
    vol_x, vol_y = 0.6, 7.65
    rounded_box(ax, (vol_x, vol_y), 4.4, 0.3, COLORS['volume_bg'],
                ec=COLORS['mysql_orange'], lw=1.2, zorder=3, style='round,pad=0.01')
    rounded_box(ax, (vol_x + 0.05, vol_y + 0.05), 0.25, 0.2, COLORS['mysql_orange'],
                ec='none', lw=0, zorder=4, style='round,pad=0.01', alpha=0.3)
    label_text(ax, vol_x + 0.175, vol_y + 0.15, 'V', fontsize=6, ha='center',
               weight='bold', color=COLORS['mysql_orange'])
    label_text(ax, vol_x + 0.4, vol_y + 0.15,
               'Volume : mysql_data  (persistance des données)', fontsize=6,
               weight='bold', color=COLORS['mysql_orange'])

    # ======================================================================
    # SECTION 2: DOCKERFILE MULTI-STAGE
    # ======================================================================
    sec2_y = 4.5
    sec2_h = 2.95
    rounded_box(ax, (0.3, sec2_y), 9.4, sec2_h, COLORS['dockerfile_bg'],
                ec='#FFD54F', lw=1.5, zorder=1, style='round,pad=0.02')

    section_title(ax, 0.7, sec2_y + sec2_h - 0.35,
                  'DOCKERFILE MULTI-STAGE', COLORS['java'], fontsize=10)

    # Stage 1: BUILD
    s1_x, s1_y = 0.7, 4.8
    s1_w, s1_h = 3.8, 2.15
    rounded_box(ax, (s1_x, s1_y), s1_w, s1_h, COLORS['white'],
                ec=COLORS['java'], lw=1.8, zorder=3, style='round,pad=0.02')

    place_logo_or_placeholder(ax, 'java', (s1_x + 0.35, s1_y + s1_h - 0.3),
                              COLORS['java'], 'Java', zoom=0.04)
    label_text(ax, s1_x + 0.6, s1_y + s1_h - 0.3,
               'Stage 1 : BUILD', fontsize=8, weight='bold', color=COLORS['java'])

    # badge
    rounded_box(ax, (s1_x + 2.2, s1_y + s1_h - 0.47), 1.4, 0.28,
                '#FFF3E0', ec=COLORS['java'], lw=0.8, zorder=4, style='round,pad=0.01')
    label_text(ax, s1_x + 2.9, s1_y + s1_h - 0.33, '≈ 400 MB',
               fontsize=6, ha='center', weight='bold', color=COLORS['java'])

    build_details = [
        'FROM eclipse-temurin:17-jdk',
        'WORKDIR /app',
        'COPY pom.xml .',
        'RUN mvn dependency:resolve',
        'COPY src ./src',
        'RUN mvn clean package -DskipTests',
    ]
    y_off = s1_y + s1_h - 0.65
    for line in build_details:
        label_text(ax, s1_x + 0.2, y_off, line, fontsize=5.2, color='#37474F',
                   style_='normal')
        y_off -= 0.2

    # Stage 2: RUNTIME
    s2_x, s2_y = 5.5, 4.8
    s2_w, s2_h = 3.8, 2.15
    rounded_box(ax, (s2_x, s2_y), s2_w, s2_h, COLORS['white'],
                ec=COLORS['spring'], lw=1.8, zorder=3, style='round,pad=0.02')

    place_logo_or_placeholder(ax, 'java', (s2_x + 0.35, s2_y + s2_h - 0.3),
                              COLORS['java_red'], 'JRE', zoom=0.04)
    label_text(ax, s2_x + 0.6, s2_y + s2_h - 0.3,
               'Stage 2 : RUNTIME', fontsize=8, weight='bold', color=COLORS['spring_dark'])

    rounded_box(ax, (s2_x + 2.2, s2_y + s2_h - 0.47), 1.4, 0.28,
                '#E8F5E9', ec=COLORS['spring'], lw=0.8, zorder=4, style='round,pad=0.01')
    label_text(ax, s2_x + 2.9, s2_y + s2_h - 0.33, '≈ 200 MB',
               fontsize=6, ha='center', weight='bold', color=COLORS['spring_dark'])

    runtime_details = [
        'FROM eclipse-temurin:17-jre',
        'WORKDIR /app',
        'COPY --from=build /app/target/*.jar app.jar',
        'EXPOSE 8080',
        'ENTRYPOINT ["java", "-jar", "app.jar"]',
    ]
    y_off = s2_y + s2_h - 0.65
    for line in runtime_details:
        label_text(ax, s2_x + 0.2, y_off, line, fontsize=5.2, color='#37474F',
                   style_='normal')
        y_off -= 0.2

    # Arrow BUILD -> RUNTIME
    draw_arrow(ax, (s1_x + s1_w, s1_y + s1_h / 2),
               (s2_x, s2_y + s2_h / 2),
               color=COLORS['java'], lw=2, style='->')
    label_text(ax, (s1_x + s1_w + s2_x) / 2, s1_y + s1_h / 2 + 0.18,
               '.jar', fontsize=7, ha='center', weight='bold', color=COLORS['java'])

    # ======================================================================
    # SECTION 3: FLUX DE DÉMARRAGE
    # ======================================================================
    sec3_y = 0.75
    sec3_h = 3.55
    rounded_box(ax, (0.3, sec3_y), 9.4, sec3_h, '#F3E5F5',
                ec='#CE93D8', lw=1.5, zorder=1, style='round,pad=0.02')

    section_title(ax, 0.7, sec3_y + sec3_h - 0.35,
                  'FLUX DE DÉMARRAGE', '#7B1FA2', fontsize=10)

    # Command box
    cmd_x, cmd_y = 0.7, 3.25
    rounded_box(ax, (cmd_x, cmd_y), 3.5, 0.38, '#4A148C',
                ec='#4A148C', lw=0, zorder=4, style='round,pad=0.01')
    label_text(ax, cmd_x + 0.15, cmd_y + 0.19,
               '$ docker-compose up -d', fontsize=7.5, weight='bold', color='#E1BEE7')

    # Flow steps
    steps = [
        ('1', 'Création du réseau bridge', COLORS['docker']),
        ('2', 'Démarrage conteneur MySQL', COLORS['mysql_blue']),
        ('3', 'Healthcheck MySQL  ✓', COLORS['spring']),
        ('4', 'Build image multi-stage (Dockerfile)', COLORS['java']),
        ('5', 'Démarrage conteneur Spring Boot', COLORS['spring']),
        ('6', 'Connexion MySQL via réseau interne', COLORS['mysql_orange']),
    ]

    step_x = 0.9
    step_y_start = 3.0
    step_spacing = 0.32

    for i, (num, text, color) in enumerate(steps):
        y = step_y_start - i * step_spacing
        # number circle
        circle = plt.Circle((step_x + 0.12, y), 0.11, fc=color, ec='white',
                             lw=1.2, zorder=5)
        ax.add_patch(circle)
        label_text(ax, step_x + 0.12, y, num, fontsize=6.5, ha='center',
                   weight='bold', color='white', zorder=12)
        label_text(ax, step_x + 0.35, y, text, fontsize=6.5, color='#37474F',
                   weight='normal')

        # vertical connector line
        if i < len(steps) - 1:
            next_y = step_y_start - (i + 1) * step_spacing
            ax.plot([step_x + 0.12, step_x + 0.12], [y - 0.11, next_y + 0.11],
                    color='#CE93D8', lw=1.2, zorder=4, ls='--')

    # Swagger & Actuator info box (right side)
    info_x, info_y = 5.3, 1.05
    info_w, info_h = 4.1, 2.8
    rounded_box(ax, (info_x, info_y), info_w, info_h, COLORS['white'],
                ec='#CE93D8', lw=1.2, zorder=3, style='round,pad=0.02')

    label_text(ax, info_x + 0.2, info_y + info_h - 0.25,
               'Points d\'accès disponibles', fontsize=7.5, weight='bold',
               color='#7B1FA2')

    # Swagger
    place_logo_or_placeholder(ax, 'swagger', (info_x + 0.4, info_y + info_h - 0.65),
                              COLORS['swagger'], 'SW', zoom=0.04)
    label_text(ax, info_x + 0.7, info_y + info_h - 0.58,
               'Swagger UI', fontsize=7, weight='bold', color='#558B2F')
    label_text(ax, info_x + 0.7, info_y + info_h - 0.78,
               'http://localhost:8080/swagger-ui.html', fontsize=5.5, color='#666')

    # Spring Actuator
    place_logo_or_placeholder(ax, 'spring', (info_x + 0.4, info_y + info_h - 1.15),
                              COLORS['spring'], 'SA', zoom=0.1)
    label_text(ax, info_x + 0.7, info_y + info_h - 1.08,
               'Actuator Health', fontsize=7, weight='bold', color=COLORS['spring_dark'])
    label_text(ax, info_x + 0.7, info_y + info_h - 1.28,
               'http://localhost:8080/actuator/health', fontsize=5.5, color='#666')

    # API
    circle_api = plt.Circle((info_x + 0.4, info_y + info_h - 1.55), 0.12,
                             fc=COLORS['docker'], ec='white', lw=1, zorder=5)
    ax.add_patch(circle_api)
    label_text(ax, info_x + 0.4, info_y + info_h - 1.55, 'API',
               fontsize=4.5, ha='center', weight='bold', color='white', zorder=12)
    label_text(ax, info_x + 0.7, info_y + info_h - 1.48,
               'API REST', fontsize=7, weight='bold', color=COLORS['docker_dark'])
    label_text(ax, info_x + 0.7, info_y + info_h - 1.68,
               'http://localhost:8080/api/users', fontsize=5.5, color='#666')

    # MySQL access
    place_logo_or_placeholder(ax, 'mysql', (info_x + 0.4, info_y + info_h - 2.05),
                              COLORS['mysql_blue'], 'My', zoom=0.04)
    label_text(ax, info_x + 0.7, info_y + info_h - 1.98,
               'MySQL Database', fontsize=7, weight='bold', color=COLORS['mysql_blue'])
    label_text(ax, info_x + 0.7, info_y + info_h - 2.18,
               'localhost:3307  (host)  /  mysql:3306  (réseau)', fontsize=5.5, color='#666')

    # ======================================================================
    # LÉGENDE DES COULEURS
    # ======================================================================
    legend_y = 0.15
    rounded_box(ax, (0.3, legend_y - 0.05), 9.4, 0.45, '#FAFAFA',
                ec='#E0E0E0', lw=0.8, zorder=1, style='round,pad=0.01')

    legend_items = [
        (COLORS['docker'], 'Docker'),
        (COLORS['mysql_blue'], 'MySQL'),
        (COLORS['spring'], 'Spring Boot'),
        (COLORS['swagger'], 'Swagger'),
        (COLORS['java'], 'Java'),
        (COLORS['env_red'], '.env / Secrets'),
    ]
    lx = 0.6
    for color, name in legend_items:
        rect = FancyBboxPatch((lx, legend_y + 0.08), 0.2, 0.2,
                              boxstyle='round,pad=0.02', fc=color, ec='none',
                              zorder=4)
        ax.add_patch(rect)
        label_text(ax, lx + 0.28, legend_y + 0.18, name, fontsize=5.5,
                   color='#555', weight='bold')
        lx += 1.55

    ax.text(5.0, legend_y - 0.0, 'Légende des couleurs',
            fontsize=5, color='#999', ha='center', va='center',
            zorder=12, fontstyle='italic')

    # ======================================================================
    # SAVE
    # ======================================================================
    plt.savefig(output_path, format='pdf', dpi=200,
                bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    print(f'✅ PDF généré : {output_path}')
    return output_path


if __name__ == '__main__':
    generate_pdf()
