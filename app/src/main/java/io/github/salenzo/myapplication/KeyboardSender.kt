package io.github.salenzo.myapplication.senders

import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothHidDevice
import android.view.KeyEvent
import kotlin.experimental.or

@Suppress("MemberVisibilityCanBePrivate")
open class KeyboardSender(
	val hidDevice: BluetoothHidDevice,
	val host: BluetoothDevice
) {
	fun keyEventHandler() {
		hidDevice.sendReport(host, 8, byteArrayOf(0, 0, 32, 0, 0, 0, 0, 0))
		hidDevice.sendReport(host, 8, byteArrayOf(0, 0, 0, 0, 0, 0, 0, 0))
	}
}

class USBKeyboardState {
	// modifiers bit 7 ---> 0
	// rightGui rightAlt rightShift rightControl leftGui leftAlt leftShift leftControl
	// modifiers, 0, key1, key2, key3, key4, key5, key6
	// https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
	companion object {
		val KeyEventMap = mapOf(
			KeyEvent.KEYCODE_A to 4,
			KeyEvent.KEYCODE_B to 5,
			KeyEvent.KEYCODE_C to 6,
			KeyEvent.KEYCODE_D to 7,
			KeyEvent.KEYCODE_E to 8,
			KeyEvent.KEYCODE_F to 9,
			KeyEvent.KEYCODE_G to 10,
			KeyEvent.KEYCODE_H to 11,
			KeyEvent.KEYCODE_I to 12,
			KeyEvent.KEYCODE_J to 13,
			KeyEvent.KEYCODE_K to 14,
			KeyEvent.KEYCODE_L to 15,
			KeyEvent.KEYCODE_M to 16,
			KeyEvent.KEYCODE_N to 17,
			KeyEvent.KEYCODE_O to 18,
			KeyEvent.KEYCODE_P to 19,
			KeyEvent.KEYCODE_Q to 20,
			KeyEvent.KEYCODE_R to 21,
			KeyEvent.KEYCODE_S to 22,
			KeyEvent.KEYCODE_T to 23,
			KeyEvent.KEYCODE_U to 24,
			KeyEvent.KEYCODE_V to 25,
			KeyEvent.KEYCODE_W to 26,
			KeyEvent.KEYCODE_X to 27,
			KeyEvent.KEYCODE_Y to 28,
			KeyEvent.KEYCODE_Z to 29,


			KeyEvent.KEYCODE_1 to 30,
			KeyEvent.KEYCODE_2 to 31,
			KeyEvent.KEYCODE_3 to 32,
			KeyEvent.KEYCODE_4 to 33,
			KeyEvent.KEYCODE_5 to 34,
			KeyEvent.KEYCODE_6 to 35,
			KeyEvent.KEYCODE_7 to 36,
			KeyEvent.KEYCODE_8 to 37,
			KeyEvent.KEYCODE_9 to 38,
			KeyEvent.KEYCODE_0 to 39,

			KeyEvent.KEYCODE_F1 to 58,
			KeyEvent.KEYCODE_F2 to 59,
			KeyEvent.KEYCODE_F3 to 60,
			KeyEvent.KEYCODE_F4 to 61,
			KeyEvent.KEYCODE_F5 to 62,
			KeyEvent.KEYCODE_F6 to 63,
			KeyEvent.KEYCODE_F7 to 64,
			KeyEvent.KEYCODE_F8 to 65,
			KeyEvent.KEYCODE_F9 to 66,
			KeyEvent.KEYCODE_F10 to 67,
			KeyEvent.KEYCODE_F11 to 68,
			KeyEvent.KEYCODE_F12 to 69,

			KeyEvent.KEYCODE_ENTER to 40,
			KeyEvent.KEYCODE_ESCAPE to 41,
			KeyEvent.KEYCODE_DEL to 42,
			KeyEvent.KEYCODE_TAB to 43,
			KeyEvent.KEYCODE_SPACE to 44,
			KeyEvent.KEYCODE_MINUS to 45,
			KeyEvent.KEYCODE_EQUALS to 46,
			KeyEvent.KEYCODE_LEFT_BRACKET to 47,
			KeyEvent.KEYCODE_RIGHT_BRACKET to 48,
			KeyEvent.KEYCODE_BACKSLASH to 49,
			KeyEvent.KEYCODE_SEMICOLON to 51,
			KeyEvent.KEYCODE_APOSTROPHE to 52,
			KeyEvent.KEYCODE_GRAVE to 53,
			KeyEvent.KEYCODE_COMMA to 54,
			KeyEvent.KEYCODE_PERIOD to 55,
			KeyEvent.KEYCODE_SLASH to 56,

			KeyEvent.KEYCODE_SCROLL_LOCK to 71,
			KeyEvent.KEYCODE_INSERT to 73,
			KeyEvent.KEYCODE_HOME to 74,
			KeyEvent.KEYCODE_PAGE_UP to 75,
			KeyEvent.KEYCODE_FORWARD_DEL to 76,
			KeyEvent.KEYCODE_MOVE_END to 77,
			KeyEvent.KEYCODE_PAGE_DOWN to 78,
			KeyEvent.KEYCODE_NUM_LOCK to 83,

			KeyEvent.KEYCODE_DPAD_RIGHT to 79,
			KeyEvent.KEYCODE_DPAD_LEFT to 80,
			KeyEvent.KEYCODE_DPAD_DOWN to 81,
			KeyEvent.KEYCODE_DPAD_UP to 82,
			KeyEvent.KEYCODE_YEN to 0x89,
			KeyEvent.KEYCODE_ZENKAKU_HANKAKU to 0x94,
			KeyEvent.KEYCODE_KANA to 0x88,
			KeyEvent.KEYCODE_KATAKANA_HIRAGANA to 0x88,
			KeyEvent.KEYCODE_HENKAN to 0x8a,
			KeyEvent.KEYCODE_MUHENKAN to 0x8b
		)
		val modifiers = intArrayOf(
			KeyEvent.KEYCODE_CTRL_LEFT,
			KeyEvent.KEYCODE_SHIFT_LEFT,
			KeyEvent.KEYCODE_ALT_LEFT,
			KeyEvent.KEYCODE_META_LEFT,
			KeyEvent.KEYCODE_CTRL_RIGHT,
			KeyEvent.KEYCODE_SHIFT_RIGHT,
			KeyEvent.KEYCODE_ALT_RIGHT,
			KeyEvent.KEYCODE_META_RIGHT
		)
	}
	var bytes = byteArrayOf(0, 0, 0, 0, 0, 0, 0, 0)
	private var q = mutableListOf<Int>()
	fun down(keyCode: Int) {
		if (q.indexOf(keyCode) < 0) q.add(keyCode)
		updateBytes()
	}
	fun up(keyCode: Int) {
		q.remove(keyCode)
		updateBytes()
	}
	fun any(): Boolean = q.size != 0
	private fun updateBytes() {
		bytes[0] = 0
		modifiers.forEachIndexed { i, keyCode ->
			if (q.indexOf(keyCode) >= 0) bytes[0] = bytes[0] or (1 shl i).toByte()
		}
		(q.filter { x -> modifiers.indexOf(x) < 0 }.mapNotNull { x -> KeyEventMap[x]?.toByte() } + listOf<Byte>(0, 0, 0, 0, 0, 0)).take(6).forEachIndexed { i, keyCode ->
			bytes[i + 2] = keyCode
		}
	}
}
