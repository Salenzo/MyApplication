package io.github.salenzo.myapplication

import android.annotation.SuppressLint
import android.annotation.TargetApi
import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothHidDevice
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.util.Log
import android.util.TypedValue
import android.view.*
import android.view.inputmethod.InputMethodManager
import android.widget.*
import io.github.salenzo.myapplication.senders.KeyboardSender
import io.github.salenzo.myapplication.senders.USBKeyboardState
import java.lang.Integer.min

// 我调用API自有分寸，要你IDE管甚么！
@Suppress("DEPRECATION")
@TargetApi(Build.VERSION_CODES.R)
@SuppressLint("ObsoleteSdkInt", "ResourceType", "ClickableViewAccessibility", "SetTextI18n")
class SelectDeviceActivity : Activity(), KeyEvent.Callback {
	private var bluetoothStatus: MenuItem? = null
	private var rKeyboardSender: KeyboardSender? = null
	private var hidd: BluetoothHidDevice? = null
	private var host: BluetoothDevice? = null
	private val state = USBKeyboardState()
	data class Key(
		val x: Int, val y: Int, val w: Int, val h: Int,
		val label: String, val keyCode: Int,
	)
	val ks = arrayOf(
		Key(0, 0, 4, 3, "\u2744", KeyEvent.KEYCODE_ESCAPE),
		Key(8, 0, 4, 3, "F1", KeyEvent.KEYCODE_F1),
		Key(12, 0, 4, 3, "F2", KeyEvent.KEYCODE_F2),
		Key(16, 0, 4, 3, "F3", KeyEvent.KEYCODE_F3),
		Key(20, 0, 4, 3, "F4", KeyEvent.KEYCODE_F4),
		Key(26, 0, 4, 3, "F5", KeyEvent.KEYCODE_F5),
		Key(30, 0, 4, 3, "F6", KeyEvent.KEYCODE_F6),
		Key(34, 0, 4, 3, "F7", KeyEvent.KEYCODE_F7),
		Key(38, 0, 4, 3, "F8", KeyEvent.KEYCODE_F8),
		Key(44, 0, 4, 3, "F9", KeyEvent.KEYCODE_F9),
		Key(48, 0, 4, 3, "F10", KeyEvent.KEYCODE_F10),
		Key(52, 0, 4, 3, "F11", KeyEvent.KEYCODE_F11),
		Key(56, 0, 4, 3, "F12", KeyEvent.KEYCODE_F12),

		Key(0, 4, 4, 4, "`", KeyEvent.KEYCODE_APOSTROPHE),
		Key(4, 4, 4, 4, "1", KeyEvent.KEYCODE_1),
		Key(8, 4, 4, 4, "2", KeyEvent.KEYCODE_2),
		Key(12, 4, 4, 4, "3", KeyEvent.KEYCODE_3),
		Key(16, 4, 4, 4, "4", KeyEvent.KEYCODE_4),
		Key(20, 4, 4, 4, "5", KeyEvent.KEYCODE_5),
		Key(24, 4, 4, 4, "6", KeyEvent.KEYCODE_6),
		Key(28, 4, 4, 4, "7", KeyEvent.KEYCODE_7),
		Key(32, 4, 4, 4, "8", KeyEvent.KEYCODE_8),
		Key(36, 4, 4, 4, "9", KeyEvent.KEYCODE_9),
		Key(40, 4, 4, 4, "0", KeyEvent.KEYCODE_0),
		Key(44, 4, 4, 4, "-", KeyEvent.KEYCODE_MINUS),
		Key(48, 4, 4, 4, "=", KeyEvent.KEYCODE_EQUALS),
		Key(52, 4, 8, 4, "\u232b", KeyEvent.KEYCODE_DEL),

		Key(0, 8, 6, 4, "\u21b9", KeyEvent.KEYCODE_TAB),
		Key(6, 8, 4, 4, "Q", KeyEvent.KEYCODE_Q),
		Key(10, 8, 4, 4, "W", KeyEvent.KEYCODE_W),
		Key(14, 8, 4, 4, "E", KeyEvent.KEYCODE_E),
		Key(18, 8, 4, 4, "R", KeyEvent.KEYCODE_R),
		Key(22, 8, 4, 4, "T", KeyEvent.KEYCODE_T),
		Key(26, 8, 4, 4, "Y", KeyEvent.KEYCODE_Y),
		Key(30, 8, 4, 4, "U", KeyEvent.KEYCODE_U),
		Key(34, 8, 4, 4, "I", KeyEvent.KEYCODE_I),
		Key(38, 8, 4, 4, "O", KeyEvent.KEYCODE_O),
		Key(42, 8, 4, 4, "P", KeyEvent.KEYCODE_P),
		Key(46, 8, 4, 4, "[", KeyEvent.KEYCODE_LEFT_BRACKET),
		Key(50, 8, 4, 4, "]", KeyEvent.KEYCODE_RIGHT_BRACKET),
		Key(54, 8, 6, 4, "\\", KeyEvent.KEYCODE_BACKSLASH),

		Key(0, 12, 7, 4, "\u2328", KeyEvent.KEYCODE_LANGUAGE_SWITCH),
		Key(7, 12, 4, 4, "A", KeyEvent.KEYCODE_A),
		Key(11, 12, 4, 4, "S", KeyEvent.KEYCODE_S),
		Key(15, 12, 4, 4, "D", KeyEvent.KEYCODE_D),
		Key(19, 12, 4, 4, "F", KeyEvent.KEYCODE_F),
		Key(23, 12, 4, 4, "G", KeyEvent.KEYCODE_G),
		Key(27, 12, 4, 4, "H", KeyEvent.KEYCODE_H),
		Key(31, 12, 4, 4, "J", KeyEvent.KEYCODE_J),
		Key(35, 12, 4, 4, "K", KeyEvent.KEYCODE_K),
		Key(39, 12, 4, 4, "L", KeyEvent.KEYCODE_L),
		Key(43, 12, 4, 4, ";", KeyEvent.KEYCODE_SEMICOLON),
		Key(47, 12, 4, 4, "'", KeyEvent.KEYCODE_APOSTROPHE),
		Key(51, 12, 9, 4, "\u21b5", KeyEvent.KEYCODE_ENTER),

		Key(0, 16, 9, 4, "\u21e7", KeyEvent.KEYCODE_SHIFT_LEFT),
		Key(9, 16, 4, 4, "Z", KeyEvent.KEYCODE_Z),
		Key(13, 16, 4, 4, "X", KeyEvent.KEYCODE_X),
		Key(17, 16, 4, 4, "C", KeyEvent.KEYCODE_C),
		Key(21, 16, 4, 4, "V", KeyEvent.KEYCODE_V),
		Key(25, 16, 4, 4, "B", KeyEvent.KEYCODE_B),
		Key(29, 16, 4, 4, "N", KeyEvent.KEYCODE_N),
		Key(33, 16, 4, 4, "M", KeyEvent.KEYCODE_M),
		Key(37, 16, 4, 4, ",", KeyEvent.KEYCODE_COMMA),
		Key(41, 16, 4, 4, ".", KeyEvent.KEYCODE_PERIOD),
		Key(45, 16, 4, 4, "/", KeyEvent.KEYCODE_SLASH),
		Key(49, 16, 11, 4, "\u21e7", KeyEvent.KEYCODE_SHIFT_RIGHT),

		Key(0, 20, 5, 4, "\u2303", KeyEvent.KEYCODE_CTRL_LEFT),
		Key(5, 20, 5, 4, "\u2318", KeyEvent.KEYCODE_META_LEFT),
		Key(10, 20, 5, 4, "\u2325", KeyEvent.KEYCODE_ALT_LEFT),
		Key(15, 20, 25, 4, "", KeyEvent.KEYCODE_SPACE),
		Key(40, 20, 5, 4, "\u2325", KeyEvent.KEYCODE_ALT_RIGHT),
		Key(45, 20, 5, 4, "\u2318", KeyEvent.KEYCODE_META_RIGHT),
		Key(50, 20, 5, 4, "\u2261", KeyEvent.KEYCODE_MENU),
		Key(55, 20, 5, 4, "\u2303", KeyEvent.KEYCODE_CTRL_RIGHT),

		Key(62, 0, 4, 3, "\u25d9", KeyEvent.KEYCODE_SYSRQ),
		Key(66, 0, 4, 3, "\u2195", KeyEvent.KEYCODE_SCROLL_LOCK),
		Key(70, 0, 4, 3, "\u203c", KeyEvent.KEYCODE_BREAK),
		Key(62, 4, 4, 4, "\u2324", KeyEvent.KEYCODE_INSERT),
		Key(62, 8, 4, 4, "\u2326", KeyEvent.KEYCODE_FORWARD_DEL),
		Key(66, 4, 4, 4, "|←", KeyEvent.KEYCODE_MOVE_HOME),
		Key(66, 8, 4, 4, "→|", KeyEvent.KEYCODE_MOVE_END),
		Key(70, 4, 4, 4, "↑↑", KeyEvent.KEYCODE_PAGE_UP),
		Key(70, 8, 4, 4, "↓↓", KeyEvent.KEYCODE_PAGE_DOWN),

		Key(66, 16, 4, 4, "↑", KeyEvent.KEYCODE_DPAD_UP),
		Key(62, 20, 4, 4, "←", KeyEvent.KEYCODE_DPAD_LEFT),
		Key(66, 20, 4, 4, "↓", KeyEvent.KEYCODE_DPAD_DOWN),
		Key(70, 20, 4, 4, "→", KeyEvent.KEYCODE_DPAD_RIGHT),

		Key(76, 4, 4, 4, "\u2115", KeyEvent.KEYCODE_NUM_LOCK),
		Key(80, 4, 4, 4, "÷", KeyEvent.KEYCODE_NUMPAD_DIVIDE),
		Key(84, 4, 4, 4, "×", KeyEvent.KEYCODE_NUMPAD_MULTIPLY),
		Key(88, 4, 4, 4, "\u2212", KeyEvent.KEYCODE_NUMPAD_SUBTRACT),
		Key(76, 8, 4, 4, "7", KeyEvent.KEYCODE_NUMPAD_7),
		Key(80, 8, 4, 4, "8", KeyEvent.KEYCODE_NUMPAD_8),
		Key(84, 8, 4, 4, "9", KeyEvent.KEYCODE_NUMPAD_9),
		Key(88, 8, 4, 8, "+", KeyEvent.KEYCODE_NUMPAD_ADD),
		Key(76, 12, 4, 4, "4", KeyEvent.KEYCODE_NUMPAD_4),
		Key(80, 12, 4, 4, "5", KeyEvent.KEYCODE_NUMPAD_5),
		Key(84, 12, 4, 4, "6", KeyEvent.KEYCODE_NUMPAD_6),
		Key(76, 16, 4, 4, "1", KeyEvent.KEYCODE_NUMPAD_1),
		Key(80, 16, 4, 4, "2", KeyEvent.KEYCODE_NUMPAD_2),
		Key(84, 16, 4, 4, "3", KeyEvent.KEYCODE_NUMPAD_3),
		Key(88, 16, 4, 8, "\u21b5", KeyEvent.KEYCODE_NUMPAD_ENTER),
		Key(76, 20, 8, 4, "0", KeyEvent.KEYCODE_NUMPAD_0),
		Key(84, 20, 4, 4, "\u00b7", KeyEvent.KEYCODE_NUMPAD_DOT),

		Key(94, 4, 4, 4, "\u2102", KeyEvent.KEYCODE_CALCULATOR),
		Key(94, 8, 4, 4, "\u266a", KeyEvent.KEYCODE_MUSIC),
		Key(94, 12, 4, 4, "\u2302", KeyEvent.KEYCODE_HOME),
		Key(94, 16, 4, 4, "\u21e6", KeyEvent.KEYCODE_NAVIGATE_PREVIOUS),
		Key(94, 20, 4, 4, "\u21e8", KeyEvent.KEYCODE_NAVIGATE_NEXT),
	)

	lateinit var sv: HorizontalScrollView

	public override fun onCreate(savedInstanceState: Bundle?) {
		super.onCreate(savedInstanceState)
		sv = HorizontalScrollView(this)
		val al = AnotherAbsoluteLayout(this)
		val tv = TextView(this).apply {
			text = "Trackpad"
			gravity = Gravity.CENTER
			layoutParams = ViewGroup.LayoutParams(114, ViewGroup.LayoutParams.MATCH_PARENT)
		}
		//al.addView(tv)
		ks.forEach { param ->
			val b = Button(this).apply {
				text = param.label
				textSize = min(param.w, param.h) * 4f
			}
			val keyCode = param.keyCode
			if (keyCode == -15) {
				b.setOnClickListener {
					b.text = "Null"
					hidd?.sendReport(host, 8, byteArrayOf(0, 0, 0, 0, 0, 0, 0, 0))
					Handler(Looper.getMainLooper()).postDelayed({
						b.text = "Alt+Tab"
						hidd?.sendReport(host, 8, byteArrayOf(0x40, 0, 0x2b, 0, 0, 0, 0, 0))
						Handler(Looper.getMainLooper()).postDelayed({
							b.text = "Alt"
							hidd?.sendReport(host, 8, byteArrayOf(0x40, 0, 0, 0, 0, 0, 0, 0))
							Handler(Looper.getMainLooper()).postDelayed({
								b.text = "Alt+Shift"
								hidd?.sendReport(host, 8, byteArrayOf(0x60, 0, 0, 0, 0, 0, 0, 0))
								Handler(Looper.getMainLooper()).postDelayed({
									b.text = "Alt+Shift+Tab"
									hidd?.sendReport(host, 8, byteArrayOf(0x60, 0, 0x2b, 0, 0, 0, 0, 0))
									Handler(Looper.getMainLooper()).postDelayed({
										b.text = "Alt+Shift"
										hidd?.sendReport(host, 8, byteArrayOf(0x60, 0, 0, 0, 0, 0, 0, 0))
										Handler(Looper.getMainLooper()).postDelayed({
											b.text = "Alt"
											hidd?.sendReport(host, 8, byteArrayOf(0x40, 0, 0, 0, 0, 0, 0, 0))
											Handler(Looper.getMainLooper()).postDelayed({
												b.text = "Alt+Enter"
												hidd?.sendReport(host, 8, byteArrayOf(0x40, 0, 0x28, 0, 0, 0, 0, 0))
												Handler(Looper.getMainLooper()).postDelayed({
													b.text = "Alt"
													hidd?.sendReport(host, 8, byteArrayOf(0x40, 0, 0, 0, 0, 0, 0, 0))
													Handler(Looper.getMainLooper()).postDelayed({
														b.text = "Null"
														hidd?.sendReport(host, 8, byteArrayOf(0, 0, 0, 0, 0, 0, 0, 0))
													}, 50)
												}, 50)
											}, 50)
										}, 50)
									}, 50)
								}, 50)
							}, 50)
						}, 50)
					}, 50)
				}
			} else {
				b.setOnTouchListener { view, event ->
					when (event.action) {
						MotionEvent.ACTION_DOWN -> {
							if (!state.any()) sv.requestDisallowInterceptTouchEvent(true)
							state.down(keyCode)
							hidd?.sendReport(host, 8, state.bytes)
							MyCompatibility.viberate(this, 6)
						}
						MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
							view.performClick()
							state.up(keyCode)
							if (!state.any()) sv.requestDisallowInterceptTouchEvent(false)
							hidd?.sendReport(host, 8, state.bytes)
						}
					}
					true
				}
			}
			al.addView(b, AnotherAbsoluteLayout.LayoutParams(
				TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 12f * param.x, resources.displayMetrics).toInt(),
				TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 12f * param.y, resources.displayMetrics).toInt(),
				TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 12f * param.w, resources.displayMetrics).toInt(),
				TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 12f * param.h, resources.displayMetrics).toInt(),
			))
		}
		sv.addView(al, ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT))
		setContentView(sv, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))

		BluetoothController.init(this)
		BluetoothController.getSender { hidd, device ->
			Log.wtf("weiufhas", "Callback called")
			Handler(mainLooper).post {
				rKeyboardSender = KeyboardSender(hidd, device)
				this.hidd = hidd
				this.host = device
				bluetoothStatus?.icon = getDrawable(R.drawable.ic_action_app_connected)
				bluetoothStatus?.tooltipText = "App Connected via bluetooth"
			}
		}
		BluetoothController.disconnectListener = {
			Handler(mainLooper).post {
				rKeyboardSender = null
				this.hidd = null
				this.host = null
				bluetoothStatus?.icon = getDrawable(R.drawable.ic_action_app_not_connected)
				bluetoothStatus?.tooltipText = "App not connected via bluetooth"
			}
		}
	}
	/*super.onPause()
	BluetoothController.btHid?.unregisterApp()
	BluetoothController.hostDevice = null
	BluetoothController.btHid = null*/

	override fun onCreateOptionsMenu(menu: Menu?): Boolean {
		menu?.add("114514")?.apply {
			setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM)
			icon = getDrawable(R.drawable.ic_action_app_not_connected)
			tooltipText = "App not connected via bluetooth"
			bluetoothStatus = this
		}
		menu?.add("软键盘")?.apply {
			icon = MyCompatibility.getDrawable(this@SelectDeviceActivity, R.drawable.ic_action_keyboard)
			setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM)
			setOnMenuItemClickListener {
				val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
				imm.toggleSoftInput(InputMethodManager.SHOW_FORCED, 0)
				true
			}
		}
		menu?.add("断开连接")?.apply {
			setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM)
			setOnMenuItemClickListener {
				BluetoothController.btHid?.disconnect(BluetoothController.hostDevice)
				bluetoothStatus?.icon = getDrawable(R.drawable.ic_action_app_not_connected)
				bluetoothStatus?.tooltipText = "App not connected via bluetooth"
				window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
				true
			}
		}
		menu?.add("启用发现")?.apply {
			setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM)
			setOnMenuItemClickListener {
				startActivityForResult(Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE), 114514)
				startActivityForResult(Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE).apply {
					putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 1145141919)
				}, 1919810)
				true
			}
		}
		menu?.add("启动服务")?.apply {
			setOnMenuItemClickListener {
				startService(Intent(this@SelectDeviceActivity, MyService::class.java))
				true
			}
		}
		menu?.add("停止服务")?.apply {
			setOnMenuItemClickListener {
				stopService(Intent(this@SelectDeviceActivity, MyService::class.java))
				true
			}
		}
		menu?.add("获取悬浮窗权限")?.apply {
			setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM)
			setOnMenuItemClickListener {
				if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this@SelectDeviceActivity)) {
					startActivityForResult(
						Intent(
							Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
							Uri.fromParts("package", packageName, null)
						), 0
					)
				}
				true
			}
		}
		menu?.add("打开悬浮窗")?.apply {
			setOnMenuItemClickListener {
				(getSystemService(WINDOW_SERVICE) as WindowManager).addView(
					TextView(this@SelectDeviceActivity).apply {
						text = "蓝牙键盘在前台（迫真）"
					},
					WindowManager.LayoutParams().apply {
						type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
							WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
						} else {
							WindowManager.LayoutParams.TYPE_PHONE
						}
						flags = WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
						width = 114
						height = 514
						alpha = 0f
					}
				)
				true
			}
		}
		menu?.add("打开无障碍设置")?.apply {
			setOnMenuItemClickListener {
				startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS).apply {
					addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
				})
				true
			}
		}
		return true
	}

	override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
		Toast.makeText(this, "请求代码${requestCode}的活动结果 = $resultCode", Toast.LENGTH_SHORT).show()
	}
}
