from flask import Flask, render_template, send_file
from flask_socketio import SocketIO

app = Flask(__name__)
app.jinja_env.auto_reload = True

io = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pattern')
def pattern():
    return render_template('pattern.html')

@app.route('/attack_range_attack.png')
def file1(): return send_file('templates/battle_common/attack_range_attack.png')
@app.route('/black_back.png')
def file2(): return send_file('templates/battle_common/black_back.png')
@app.route('/btn_cancel.png')
def file3(): return send_file('templates/battle_common/btn_cancel.png')
@app.route('/btn_cancel_bkg.png')
def file4(): return send_file('templates/battle_common/btn_cancel_bkg.png')
@app.route('/btn_confirm_bkg.png')
def file5(): return send_file('templates/battle_common/btn_confirm_bkg.png')
@app.route('/btn_drag_back.png')
def file6(): return send_file('templates/battle_common/btn_drag_back.png')
@app.route('/btn_escape.png')
def file7(): return send_file('templates/battle_common/btn_escape.png')
@app.route('/btn_pause.png')
def file8(): return send_file('templates/battle_common/btn_pause.png')
@app.route('/btn_play.png')
def file9(): return send_file('templates/battle_common/btn_play.png')
@app.route('/btn_range.png')
def file10(): return send_file('templates/battle_common/btn_range.png')
@app.route('/btn_speed_0x.png')
def file11(): return send_file('templates/battle_common/btn_speed_0x.png')
@app.route('/btn_speed_1x.png')
def file12(): return send_file('templates/battle_common/btn_speed_1x.png')
@app.route('/btn_speed_2x.png')
def file13(): return send_file('templates/battle_common/btn_speed_2x.png')
@app.route('/btn_speed_3x.png')
def file14(): return send_file('templates/battle_common/btn_speed_3x.png')
@app.route('/btn_system.png')
def file15(): return send_file('templates/battle_common/btn_system.png')
@app.route('/Default-Particle.png')
def file16(): return send_file('templates/battle_common/Default-Particle.png')
@app.route('/enemy_1526_sfsui.png')
def file17(): return send_file('templates/battle_common/enemy_1526_sfsui.png')
@app.route('/icon_ap_protect.png')
def file18(): return send_file('templates/battle_common/icon_ap_protect.png')
@app.route('/icon_evolve_0.png')
def file19(): return send_file('templates/battle_common/icon_evolve_0.png')
@app.route('/icon_evolve_1.png')
def file20(): return send_file('templates/battle_common/icon_evolve_1.png')
@app.route('/icon_evolve_2.png')
def file21(): return send_file('templates/battle_common/icon_evolve_2.png')
@app.route('/icon_evolve_3.png')
def file22(): return send_file('templates/battle_common/icon_evolve_3.png')
@app.route('/icon_item_AP.png')
def file23(): return send_file('templates/battle_common/icon_item_AP.png')
@app.route('/icon_item_bkg.png')
def file24(): return send_file('templates/battle_common/icon_item_bkg.png')
@app.route('/icon_lv_not_enough.png')
def file25(): return send_file('templates/battle_common/icon_lv_not_enough.png')
@app.route('/icon_profession_caster.png')
def file26(): return send_file('templates/battle_common/icon_profession_caster.png')
@app.route('/icon_profession_caster_lighten.png')
def file27(): return send_file('templates/battle_common/icon_profession_caster_lighten.png')
@app.route('/icon_profession_medic.png')
def file28(): return send_file('templates/battle_common/icon_profession_medic.png')
@app.route('/icon_profession_medic_lighten.png')
def file29(): return send_file('templates/battle_common/icon_profession_medic_lighten.png')
@app.route('/icon_profession_pioneer.png')
def file30(): return send_file('templates/battle_common/icon_profession_pioneer.png')
@app.route('/icon_profession_pioneer_lighten.png')
def file31(): return send_file('templates/battle_common/icon_profession_pioneer_lighten.png')
@app.route('/icon_profession_sniper.png')
def file32(): return send_file('templates/battle_common/icon_profession_sniper.png')
@app.route('/icon_profession_sniper_lighten.png')
def file33(): return send_file('templates/battle_common/icon_profession_sniper_lighten.png')
@app.route('/icon_profession_special.png')
def file34(): return send_file('templates/battle_common/icon_profession_special.png')
@app.route('/icon_profession_special_lighten.png')
def file35(): return send_file('templates/battle_common/icon_profession_special_lighten.png')
@app.route('/icon_profession_support.png')
def file36(): return send_file('templates/battle_common/icon_profession_support.png')
@app.route('/icon_profession_support_lighten.png')
def file37(): return send_file('templates/battle_common/icon_profession_support_lighten.png')
@app.route('/icon_profession_tank.png')
def file38(): return send_file('templates/battle_common/icon_profession_tank.png')
@app.route('/icon_profession_tank_lighten.png')
def file39(): return send_file('templates/battle_common/icon_profession_tank_lighten.png')
@app.route('/icon_profession_token.png')
def file40(): return send_file('templates/battle_common/icon_profession_token.png')
@app.route('/icon_profession_token_lighten.png')
def file41(): return send_file('templates/battle_common/icon_profession_token_lighten.png')
@app.route('/icon_profession_warrior.png')
def file42(): return send_file('templates/battle_common/icon_profession_warrior.png')
@app.route('/icon_profession_warrior_lighten.png')
def file43(): return send_file('templates/battle_common/icon_profession_warrior_lighten.png')
@app.route('/icon_PRTS.png')
def file44(): return send_file('templates/battle_common/icon_PRTS.png')
@app.route('/icon_state_alert.png')
def file45(): return send_file('templates/battle_common/icon_state_alert.png')
@app.route('/icon_state_normal_inner.png')
def file46(): return send_file('templates/battle_common/icon_state_normal_inner.png')
@app.route('/icon_state_normal_outside.png')
def file47(): return send_file('templates/battle_common/icon_state_normal_outside.png')
@app.route('/image_ap_back.png')
def file48(): return send_file('templates/battle_common/image_ap_back.png')
@app.route('/image_bak.png')
def file49(): return send_file('templates/battle_common/image_bak.png')
@app.route('/image_bkg_ap_protect.png')
def file50(): return send_file('templates/battle_common/image_bkg_ap_protect.png')
@app.route('/image_bkg_ps_not_enough.png')
def file51(): return send_file('templates/battle_common/image_bkg_ps_not_enough.png')
@app.route('/image_btn_bkg_black.png')
def file52(): return send_file('templates/battle_common/image_btn_bkg_black.png')
@app.route('/image_btn_bkg_blue.png')
def file53(): return send_file('templates/battle_common/image_btn_bkg_blue.png')
@app.route('/image_round_corner_bkg.png')
def file54(): return send_file('templates/battle_common/image_round_corner_bkg.png')
@app.route('/image_skill_duration_bkg.png')
def file55(): return send_file('templates/battle_common/image_skill_duration_bkg.png')
@app.route('/image_skill_tag_bkg.png')
def file56(): return send_file('templates/battle_common/image_skill_tag_bkg.png')
@app.route('/img_dark_ftg.png')
def file57(): return send_file('templates/battle_common/img_dark_ftg.png')
@app.route('/projectile_yuki_boc#2.png')
def file58(): return send_file('templates/battle_common/projectile_yuki_boc#2.png')
@app.route('/sample_practice.png')
def file59(): return send_file('templates/battle_common/sample_practice.png')
@app.route('/slider_ep_back.png')
def file60(): return send_file('templates/battle_common/slider_ep_back.png')
@app.route('/slider_ep_fill.png')
def file61(): return send_file('templates/battle_common/slider_ep_fill.png')
@app.route('/slider_hp_back.png')
def file62(): return send_file('templates/battle_common/slider_hp_back.png')
@app.route('/slider_hp_fill.png')
def file63(): return send_file('templates/battle_common/slider_hp_fill.png')
@app.route('/slider_sp_back.png')
def file64(): return send_file('templates/battle_common/slider_sp_back.png')
@app.route('/slider_sp_fill.png')
def file65(): return send_file('templates/battle_common/slider_sp_fill.png')
@app.route('/SpriteAtlasTexture-UI_BATTLE_LOADING-1024x1024-fmt34.png')
def file66(): return send_file('templates/battle_common/SpriteAtlasTexture-UI_BATTLE_LOADING-1024x1024-fmt34.png')
@app.route('/sprite_assist_char.png')
def file67(): return send_file('templates/battle_common/sprite_assist_char.png')
@app.route('/sprite_attack_range.png')
def file68(): return send_file('templates/battle_common/sprite_attack_range.png')
@app.route('/sprite_auto.png')
def file69(): return send_file('templates/battle_common/sprite_auto.png')
@app.route('/sprite_auto_battle_label.png')
def file70(): return send_file('templates/battle_common/sprite_auto_battle_label.png')
@app.route('/sprite_back_shadow.png')
def file71(): return send_file('templates/battle_common/sprite_back_shadow.png')
@app.route('/sprite_base_hp.png')
def file72(): return send_file('templates/battle_common/sprite_base_hp.png')
@app.route('/sprite_battlemenu_frame.txt.png')
def file73(): return send_file('templates/battle_common/sprite_battlemenu_frame.txt.png')
@app.route('/sprite_bg.png')
def file74(): return send_file('templates/battle_common/sprite_bg.png')
@app.route('/sprite_bkg_lv_not_enough.png')
def file75(): return send_file('templates/battle_common/sprite_bkg_lv_not_enough.png')
@app.route('/sprite_charactercard_choesn.png')
def file76(): return send_file('templates/battle_common/sprite_charactercard_choesn.png')
@app.route('/sprite_character_info_shadow.png')
def file77(): return send_file('templates/battle_common/sprite_character_info_shadow.png')
@app.route('/sprite_character_menu_frame.txt.png')
def file78(): return send_file('templates/battle_common/sprite_character_menu_frame.txt.png')
@app.route('/sprite_circle.png')
def file79(): return send_file('templates/battle_common/sprite_circle.png')
@app.route('/sprite_combo_icon.png')
def file80(): return send_file('templates/battle_common/sprite_combo_icon.png')
@app.route('/sprite_combo_outline.png')
def file81(): return send_file('templates/battle_common/sprite_combo_outline.png')
@app.route('/sprite_combo_under.png')
def file82(): return send_file('templates/battle_common/sprite_combo_under.png')
@app.route('/sprite_cost #1852.png')
def file83(): return send_file('templates/battle_common/sprite_cost #1852.png')
@app.route('/sprite_cost #957.png')
def file84(): return send_file('templates/battle_common/sprite_cost #957.png')
@app.route('/sprite_cost.png')
def file85(): return send_file('templates/battle_common/sprite_cost.png')
@app.route('/sprite_cost_back.txt.png')
def file86(): return send_file('templates/battle_common/sprite_cost_back.txt.png')
@app.route('/sprite_cost_slider_back.png')
def file87(): return send_file('templates/battle_common/sprite_cost_slider_back.png')
@app.route('/sprite_cost_slider_fill.png')
def file88(): return send_file('templates/battle_common/sprite_cost_slider_fill.png')
@app.route('/sprite_direction_arrow.png')
def file89(): return send_file('templates/battle_common/sprite_direction_arrow.png')
@app.route('/sprite_direction_thumb.png')
def file90(): return send_file('templates/battle_common/sprite_direction_thumb.png')
@app.route('/sprite_enemy_boss_avatar_bg.png')
def file91(): return send_file('templates/battle_common/sprite_enemy_boss_avatar_bg.png')
@app.route('/sprite_enemy_boss_hp_bg.png')
def file92(): return send_file('templates/battle_common/sprite_enemy_boss_hp_bg.png')
@app.route('/sprite_enemy_boss_hp_hit_effect.png')
def file93(): return send_file('templates/battle_common/sprite_enemy_boss_hp_hit_effect.png')
@app.route('/sprite_enemy_new.png')
def file94(): return send_file('templates/battle_common/sprite_enemy_new.png')
@app.route('/sprite_enemy_toast_back_process.png')
def file95(): return send_file('templates/battle_common/sprite_enemy_toast_back_process.png')
@app.route('/sprite_enemy_toast_process.png')
def file96(): return send_file('templates/battle_common/sprite_enemy_toast_process.png')
@app.route('/sprite_ep_color.png')
def file97(): return send_file('templates/battle_common/sprite_ep_color.png')
@app.route('/sprite_ep_fire_icon.png')
def file98(): return send_file('templates/battle_common/sprite_ep_fire_icon.png')
@app.route('/sprite_ep_fire_icon.txt.png')
def file99(): return send_file('templates/battle_common/sprite_ep_fire_icon.txt.png')
@app.route('/sprite_ep_hit_spread.png')
def file100(): return send_file('templates/battle_common/sprite_ep_hit_spread.png')
@app.route('/sprite_ep_icon.png')
def file101(): return send_file('templates/battle_common/sprite_ep_icon.png')
@app.route('/sprite_ep_water_icon.png')
def file102(): return send_file('templates/battle_common/sprite_ep_water_icon.png')
@app.route('/sprite_error_slider.png')
def file103(): return send_file('templates/battle_common/sprite_error_slider.png')
@app.route('/sprite_frame.png')
def file104(): return send_file('templates/battle_common/sprite_frame.png')
@app.route('/sprite_hint_default.png')
def file105(): return send_file('templates/battle_common/sprite_hint_default.png')
@app.route('/sprite_hint_error.png')
def file106(): return send_file('templates/battle_common/sprite_hint_error.png')
@app.route('/sprite_hp_thumb.png')
def file107(): return send_file('templates/battle_common/sprite_hp_thumb.png')
@app.route('/sprite_illust_shadow.png')
def file108(): return send_file('templates/battle_common/sprite_illust_shadow.png')
@app.route('/sprite_info_bar_2part.png')
def file109(): return send_file('templates/battle_common/sprite_info_bar_2part.png')
@app.route('/sprite_info_bar_3part.png')
def file110(): return send_file('templates/battle_common/sprite_info_bar_3part.png')
@app.route('/sprite_info_popup_back.png')
def file111(): return send_file('templates/battle_common/sprite_info_popup_back.png')
@app.route('/sprite_kill_new.png')
def file112(): return send_file('templates/battle_common/sprite_kill_new.png')
@app.route('/sprite_lost_person.png')
def file113(): return send_file('templates/battle_common/sprite_lost_person.png')
@app.route('/sprite_lost_shield.png')
def file114(): return send_file('templates/battle_common/sprite_lost_shield.png')
@app.route('/sprite_mission_accomplished.png')
def file115(): return send_file('templates/battle_common/sprite_mission_accomplished.png')
@app.route('/sprite_practice.png')
def file116(): return send_file('templates/battle_common/sprite_practice.png')
@app.route('/sprite_practice_2.png')
def file117(): return send_file('templates/battle_common/sprite_practice_2.png')
@app.route('/sprite_profession_bar.png')
def file118(): return send_file('templates/battle_common/sprite_profession_bar.png')
@app.route('/sprite_profession_shadow.png')
def file119(): return send_file('templates/battle_common/sprite_profession_shadow.png')
@app.route('/sprite_progress_thumb.png')
def file120(): return send_file('templates/battle_common/sprite_progress_thumb.png')
@app.route('/sprite_rarity_1-4.png')
def file121(): return send_file('templates/battle_common/sprite_rarity_1-4.png')
@app.route('/sprite_rarity_5.png')
def file122(): return send_file('templates/battle_common/sprite_rarity_5.png')
@app.route('/sprite_rarity_6.png')
def file123(): return send_file('templates/battle_common/sprite_rarity_6.png')
@app.route('/sprite_red_ftg.png')
def file124(): return send_file('templates/battle_common/sprite_red_ftg.png')
@app.route('/sprite_remaining_back.png')
def file125(): return send_file('templates/battle_common/sprite_remaining_back.png')
@app.route('/sprite_respawn_ring.png')
def file126(): return send_file('templates/battle_common/sprite_respawn_ring.png')
@app.route('/sprite_skill_amount.txt.png')
def file127(): return send_file('templates/battle_common/sprite_skill_amount.txt.png')
@app.route('/sprite_skill_bg.png')
def file128(): return send_file('templates/battle_common/sprite_skill_bg.png')
@app.route('/sprite_skill_bullet.png')
def file129(): return send_file('templates/battle_common/sprite_skill_bullet.png')
@app.route('/sprite_skill_notready.png')
def file130(): return send_file('templates/battle_common/sprite_skill_notready.png')
@app.route('/sprite_skill_range_off.png')
def file131(): return send_file('templates/battle_common/sprite_skill_range_off.png')
@app.route('/sprite_skill_range_on.png')
def file132(): return send_file('templates/battle_common/sprite_skill_range_on.png')
@app.route('/sprite_skill_ready #702.png')
def file133(): return send_file('templates/battle_common/sprite_skill_ready #702.png')
@app.route('/sprite_skill_ready.png')
def file134(): return send_file('templates/battle_common/sprite_skill_ready.png')
@app.route('/sprite_skill_ready_not_full.png')
def file135(): return send_file('templates/battle_common/sprite_skill_ready_not_full.png')
@app.route('/sprite_skill_stop #1998.png')
def file136(): return send_file('templates/battle_common/sprite_skill_stop #1998.png')
@app.route('/sprite_skill_stop.png')
def file137(): return send_file('templates/battle_common/sprite_skill_stop.png')
@app.route('/sprite_sp_thumb.png')
def file138(): return send_file('templates/battle_common/sprite_sp_thumb.png')
@app.route('/sprite_takeover.png')
def file139(): return send_file('templates/battle_common/sprite_takeover.png')
@app.route('/sprite_toast_close.png')
def file140(): return send_file('templates/battle_common/sprite_toast_close.png')
@app.route('/sprite_toast_pause.png')
def file141(): return send_file('templates/battle_common/sprite_toast_pause.png')
@app.route('/text_back_alpha_80.png')
def file142(): return send_file('templates/battle_common/text_back_alpha_80.png')
@app.route('/toast_enemy_pop_back.png')
def file143(): return send_file('templates/battle_common/toast_enemy_pop_back.png')
@app.route('/trail_11.png')
def file144(): return send_file('templates/battle_common/trail_11.png')

@io.on('connect')
def connect():
    print('connect')


@io.on('disconnect')
def disconnect():
    print('disconnect')


t = 1


@io.on('update')
def update():
    global t
    t += 1
    io.emit('update', t)


if __name__ == '__main__':
    io.run(app, debug=True)
