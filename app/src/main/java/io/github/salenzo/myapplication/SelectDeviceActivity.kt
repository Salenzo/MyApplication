package io.github.salenzo.myapplication

import android.annotation.SuppressLint
import android.app.Activity
import android.app.NotificationManager
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothHidDevice
import android.content.Context
import android.content.Intent
import android.content.res.Resources
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.media.Image
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
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
import java.nio.ByteBuffer

@Suppress("DEPRECATION")
@SuppressLint("ObsoleteSdkInt", "ResourceType", "ClickableViewAccessibility", "SetTextI18n")
class SelectDeviceActivity : Activity(), KeyEvent.Callback {
	private var bluetoothStatus: MenuItem? = null
	private var rKeyboardSender: KeyboardSender? = null
	private var hidd: BluetoothHidDevice? = null
	private var host: BluetoothDevice? = null
	private val state = USBKeyboardState()
	companion object {
		var mMediaProjection: MediaProjection? = null
		val mImageReader = ImageReader.newInstance(
			1920,
			1080,
			PixelFormat.RGBA_8888,  //此处必须和下面 buffer处理一致的格式 ，RGB_565在一些机器上出现兼容问题。
			10
		)
		fun deimg(): Bitmap? {
			if (mMediaProjection == null) return null
			val img = mImageReader.acquireLatestImage()
			if (img == null) return null
			val width: Int = img.getWidth()
			val height: Int = img.getHeight()
			val planes: Array<Image.Plane> = img.getPlanes()
			val buffer: ByteBuffer = planes[0].getBuffer()
			val pixelStride: Int = planes[0].getPixelStride()
			val rowStride: Int = planes[0].getRowStride()
			val rowPadding = rowStride - pixelStride * width
			val bitmap = Bitmap.createBitmap(
				width + rowPadding / pixelStride, height,
				Bitmap.Config.ARGB_8888
			)
			bitmap.copyPixelsFromBuffer(buffer)
			img.close()
			return bitmap
		}
	}
	val ks = arrayOf(
		intArrayOf(Int.MIN_VALUE, Int.MIN_VALUE, 4, 3, 0x2744, KeyEvent.KEYCODE_ESCAPE),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, Int.MIN_VALUE, Int.MIN_VALUE),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x2474, KeyEvent.KEYCODE_F1),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x2475, KeyEvent.KEYCODE_F2),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x2476, KeyEvent.KEYCODE_F3),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x2477, KeyEvent.KEYCODE_F4),
		intArrayOf(-1, Int.MIN_VALUE, 2, 3, Int.MIN_VALUE, Int.MIN_VALUE),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x2478, KeyEvent.KEYCODE_F5),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x2479, KeyEvent.KEYCODE_F6),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x247a, KeyEvent.KEYCODE_F7),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x247b, KeyEvent.KEYCODE_F8),
		intArrayOf(-1, Int.MIN_VALUE, 2, 3, Int.MIN_VALUE, Int.MIN_VALUE),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x247c, KeyEvent.KEYCODE_F9),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x247d, KeyEvent.KEYCODE_F10),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x247e, KeyEvent.KEYCODE_F11),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x247f, KeyEvent.KEYCODE_F12),

		intArrayOf(Int.MIN_VALUE, 1, 4, 4, 0x60, KeyEvent.KEYCODE_APOSTROPHE),
		intArrayOf(-1, 1, 4, 4, 0x31, KeyEvent.KEYCODE_1),
		intArrayOf(-1, 1, 4, 4, 0x32, KeyEvent.KEYCODE_2),
		intArrayOf(-1, 1, 4, 4, 0x33, KeyEvent.KEYCODE_3),
		intArrayOf(-1, 1, 4, 4, 0x34, KeyEvent.KEYCODE_4),
		intArrayOf(-1, 1, 4, 4, 0x35, KeyEvent.KEYCODE_5),
		intArrayOf(-1, 1, 4, 4, 0x36, KeyEvent.KEYCODE_6),
		intArrayOf(-1, 1, 4, 4, 0x37, KeyEvent.KEYCODE_7),
		intArrayOf(-1, 1, 4, 4, 0x38, KeyEvent.KEYCODE_8),
		intArrayOf(-1, 1, 4, 4, 0x39, KeyEvent.KEYCODE_9),
		intArrayOf(-1, 1, 4, 4, 0x30, KeyEvent.KEYCODE_0),
		intArrayOf(-1, 1, 4, 4, 0x2d, KeyEvent.KEYCODE_MINUS),
		intArrayOf(-1, 1, 4, 4, 0x3d, KeyEvent.KEYCODE_EQUALS),
		intArrayOf(-1, 1, 8, 4, 0x232b, KeyEvent.KEYCODE_DEL),

		intArrayOf(Int.MIN_VALUE, 20, 6, 4, 0x21b9, KeyEvent.KEYCODE_TAB),
		intArrayOf(-1, 20, 4, 4, 0x51, KeyEvent.KEYCODE_Q),
		intArrayOf(-1, 20, 4, 4, 0x57, KeyEvent.KEYCODE_W),
		intArrayOf(-1, 20, 4, 4, 0x45, KeyEvent.KEYCODE_E),
		intArrayOf(-1, 20, 4, 4, 0x52, KeyEvent.KEYCODE_R),
		intArrayOf(-1, 20, 4, 4, 0x54, KeyEvent.KEYCODE_T),
		intArrayOf(-1, 20, 4, 4, 0x59, KeyEvent.KEYCODE_Y),
		intArrayOf(-1, 20, 4, 4, 0x55, KeyEvent.KEYCODE_U),
		intArrayOf(-1, 20, 4, 4, 0x49, KeyEvent.KEYCODE_I),
		intArrayOf(-1, 20, 4, 4, 0x4f, KeyEvent.KEYCODE_O),
		intArrayOf(-1, 20, 4, 4, 0x50, KeyEvent.KEYCODE_P),
		intArrayOf(-1, 20, 4, 4, 0x5b, KeyEvent.KEYCODE_LEFT_BRACKET),
		intArrayOf(-1, 20, 4, 4, 0x5d, KeyEvent.KEYCODE_RIGHT_BRACKET),
		intArrayOf(-1, 20, 6, 4, 0x5c, KeyEvent.KEYCODE_BACKSLASH),

		intArrayOf(Int.MIN_VALUE, 30, 7, 4, 0x2328, KeyEvent.KEYCODE_LANGUAGE_SWITCH),
		intArrayOf(-1, 30, 4, 4, 0x41, KeyEvent.KEYCODE_A),
		intArrayOf(-1, 30, 4, 4, 0x53, KeyEvent.KEYCODE_S),
		intArrayOf(-1, 30, 4, 4, 0x44, KeyEvent.KEYCODE_D),
		intArrayOf(-1, 30, 4, 4, 0x46, KeyEvent.KEYCODE_F),
		intArrayOf(-1, 30, 4, 4, 0x47, KeyEvent.KEYCODE_G),
		intArrayOf(-1, 30, 4, 4, 0x48, KeyEvent.KEYCODE_H),
		intArrayOf(-1, 30, 4, 4, 0x4a, KeyEvent.KEYCODE_J),
		intArrayOf(-1, 30, 4, 4, 0x4b, KeyEvent.KEYCODE_K),
		intArrayOf(-1, 30, 4, 4, 0x4c, KeyEvent.KEYCODE_L),
		intArrayOf(-1, 30, 4, 4, 0x3b, KeyEvent.KEYCODE_SEMICOLON),
		intArrayOf(-1, 30, 4, 4, 0x27, KeyEvent.KEYCODE_APOSTROPHE),
		intArrayOf(-1, 30, 9, 4, 0x21b5, KeyEvent.KEYCODE_ENTER),

		intArrayOf(Int.MIN_VALUE, 50, 9, 4, 0x21e7, KeyEvent.KEYCODE_SHIFT_LEFT),
		intArrayOf(-1, 50, 4, 4, 0x5a, KeyEvent.KEYCODE_Z),
		intArrayOf(-1, 50, 4, 4, 0x58, KeyEvent.KEYCODE_X),
		intArrayOf(-1, 50, 4, 4, 0x43, KeyEvent.KEYCODE_C),
		intArrayOf(-1, 50, 4, 4, 0x56, KeyEvent.KEYCODE_V),
		intArrayOf(-1, 50, 4, 4, 0x42, KeyEvent.KEYCODE_B),
		intArrayOf(-1, 50, 4, 4, 0x4e, KeyEvent.KEYCODE_N),
		intArrayOf(-1, 50, 4, 4, 0x4d, KeyEvent.KEYCODE_M),
		intArrayOf(-1, 50, 4, 4, 0x2c, KeyEvent.KEYCODE_COMMA),
		intArrayOf(-1, 50, 4, 4, 0x2e, KeyEvent.KEYCODE_PERIOD),
		intArrayOf(-1, 50, 4, 4, 0x2f, KeyEvent.KEYCODE_SLASH),
		intArrayOf(-1, 50, 11, 4, 0x21e7, KeyEvent.KEYCODE_SHIFT_RIGHT),

		intArrayOf(Int.MIN_VALUE, 60, 5, 4, 0x2303, KeyEvent.KEYCODE_CTRL_LEFT),
		intArrayOf(-1, 60, 5, 4, 0x2318, KeyEvent.KEYCODE_META_LEFT),
		intArrayOf(-1, 60, 5, 4, 0x2325, KeyEvent.KEYCODE_ALT_LEFT),
		intArrayOf(-1, 60, 25, 4, 0x20, KeyEvent.KEYCODE_SPACE),
		intArrayOf(-1, 60, 5, 4, 0x2325, KeyEvent.KEYCODE_ALT_RIGHT),
		intArrayOf(-1, 60, 5, 4, 0x2318, KeyEvent.KEYCODE_META_RIGHT),
		intArrayOf(-1, 60, 5, 4, 0x2261, KeyEvent.KEYCODE_MENU),
		intArrayOf(-1, 60, 5, 4, 0x2303, KeyEvent.KEYCODE_CTRL_RIGHT),

		intArrayOf(-1, Int.MIN_VALUE, 2, 20, Int.MIN_VALUE, Int.MIN_VALUE),

		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x25d9, KeyEvent.KEYCODE_SYSRQ),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x2195, KeyEvent.KEYCODE_SCROLL_LOCK),
		intArrayOf(-1, Int.MIN_VALUE, 4, 3, 0x203c, KeyEvent.KEYCODE_BREAK),
		intArrayOf(77, 1, 4, 4, 0x2324, KeyEvent.KEYCODE_INSERT),
		intArrayOf(-1, 1, 4, 4, 0x21e4, KeyEvent.KEYCODE_MOVE_HOME),
		intArrayOf(-1, 1, 4, 4, 0x21c8, KeyEvent.KEYCODE_PAGE_UP),
		intArrayOf(77, 20, 4, 4, 0x2326, KeyEvent.KEYCODE_FORWARD_DEL),
		intArrayOf(-1, 20, 4, 4, 0x21e5, KeyEvent.KEYCODE_MOVE_END),
		intArrayOf(-1, 20, 4, 4, 0x21ca, KeyEvent.KEYCODE_PAGE_DOWN),
		intArrayOf(77, -1, 4, 4, Int.MIN_VALUE, Int.MIN_VALUE),
		intArrayOf(-1, -1, 4, 4, 0x2191, KeyEvent.KEYCODE_DPAD_UP),
		intArrayOf(77, 60, 4, 4, 0x2190, KeyEvent.KEYCODE_DPAD_LEFT),
		intArrayOf(-1, 60, 4, 4, 0x2193, KeyEvent.KEYCODE_DPAD_DOWN),
		intArrayOf(-1, 60, 4, 4, 0x2192, KeyEvent.KEYCODE_DPAD_RIGHT),

		intArrayOf(-1, Int.MIN_VALUE, 2, 20, Int.MIN_VALUE, Int.MIN_VALUE),

		intArrayOf(-1, 1, 4, 4, 0x2115, KeyEvent.KEYCODE_NUM_LOCK),
		intArrayOf(-1, 1, 4, 4, 0xf7, KeyEvent.KEYCODE_NUMPAD_DIVIDE),
		intArrayOf(-1, 1, 4, 4, 0xd7, KeyEvent.KEYCODE_NUMPAD_MULTIPLY),
		intArrayOf(-1, 1, 4, 4, 0x2212, KeyEvent.KEYCODE_NUMPAD_SUBTRACT),
		intArrayOf(92, 20, 4, 4, 0x37, KeyEvent.KEYCODE_NUMPAD_7),
		intArrayOf(-1, 20, 4, 4, 0x38, KeyEvent.KEYCODE_NUMPAD_8),
		intArrayOf(-1, 20, 4, 4, 0x38, KeyEvent.KEYCODE_NUMPAD_9),
		intArrayOf(-1, 20, 4, 8, 0x2b, KeyEvent.KEYCODE_NUMPAD_ADD),
		intArrayOf(92, 30, 4, 4, 0x34, KeyEvent.KEYCODE_NUMPAD_4),
		intArrayOf(-1, 30, 4, 4, 0x35, KeyEvent.KEYCODE_NUMPAD_5),
		intArrayOf(-1, 30, 4, 4, 0x36, KeyEvent.KEYCODE_NUMPAD_6),
		intArrayOf(92, 50, 4, 4, 0x31, KeyEvent.KEYCODE_NUMPAD_1),
		intArrayOf(-1, 50, 4, 4, 0x32, KeyEvent.KEYCODE_NUMPAD_2),
		intArrayOf(-1, 50, 4, 4, 0x33, KeyEvent.KEYCODE_NUMPAD_3),
		intArrayOf(-1, 50, 4, 8, 0x21b5, KeyEvent.KEYCODE_NUMPAD_ENTER),
		intArrayOf(92, 60, 8, 4, 0x30, KeyEvent.KEYCODE_NUMPAD_0),
		intArrayOf(-1, 60, 4, 4, 0xb7, KeyEvent.KEYCODE_NUMPAD_DOT),

		intArrayOf(-1, Int.MIN_VALUE, 6, 20, Int.MIN_VALUE, Int.MIN_VALUE),

		intArrayOf(-1, 1, 4, 4, 0x2102, KeyEvent.KEYCODE_CALCULATOR),
		intArrayOf(-1, 1, 4, 4, 0x266a, KeyEvent.KEYCODE_MUSIC),
		intArrayOf(-1, 1, 4, 4, 0x2302, KeyEvent.KEYCODE_HOME),
		intArrayOf(-1, 1, 4, 4, 0x21e6, KeyEvent.KEYCODE_NAVIGATE_PREVIOUS),
		intArrayOf(-1, 1, 4, 4, 0x21e8, KeyEvent.KEYCODE_NAVIGATE_NEXT),

		//intArrayOf(Int.MIN_VALUE, -1, 20, 4, 0x61, -15)
	)

	lateinit var sv: HorizontalScrollView

	public override fun onCreate(savedInstanceState: Bundle?) {
		super.onCreate(savedInstanceState)
		sv = HorizontalScrollView(this)
		val rl = RelativeLayout(this)
		val tv = TextView(this)
		tv.text = "Trackpad"
		tv.gravity = Gravity.CENTER
		tv.layoutParams = ViewGroup.LayoutParams(114, ViewGroup.LayoutParams.MATCH_PARENT)
		//rl.addView(tv)
		ks.forEachIndexed { i, param ->
			Log.d("www", "[${i}] = ${param.contentToString()}, '${param[4].toChar()}'")
			val rllp = RelativeLayout.LayoutParams(
				TypedValue.applyDimension(
					TypedValue.COMPLEX_UNIT_DIP,
					12f * param[2],
					resources.displayMetrics
				).toInt(),
				TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 12f * param[3], resources.displayMetrics).toInt()
			)
			if (param[0] != Int.MIN_VALUE) {
				var id = param[0] + 114514
				if (param[0] < 0) id += i
				rllp.addRule(RelativeLayout.RIGHT_OF, id)
			}
			if (param[1] != Int.MIN_VALUE) {
				var id = param[1] + 114514
				if (param[1] < 0) id += i
				rllp.addRule(RelativeLayout.BELOW, id)
			}
			if (param[4] == Int.MIN_VALUE) {
				val v = TextView(this)
				v.id = i + 114514
				rl.addView(v, rllp)
			} else {
				val b = Button(this)
				b.id = i + 114514
				b.text = param[4].toChar().toString()
				b.textSize = min(param[2], param[3]) * 4f
				val keyCode = param[5]
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
				rl.addView(b, rllp)
			}
		}
		sv.addView(rl, ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT))
		setContentView(
			sv,
			ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
		)
	}

	public override fun onStart() {
		super.onStart()

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

	public override fun onResume() {
		super.onResume()
	}

	public override fun onPause() {
		super.onPause()
		/*BluetoothController.btHid?.unregisterApp()
		BluetoothController.hostDevice = null
		BluetoothController.btHid = null*/
	}

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
		menu?.add("获取截屏权限")?.apply {
			setOnMenuItemClickListener {
				if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
					if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O && getSystemService(NotificationManager::class.java).activeNotifications.none { it.notification.channelId == "２５５６５" }) {
						Toast.makeText(this@SelectDeviceActivity, "媒体投射要求前台服务正在运行，这在本应用中与无障碍服务合并。准备好后，再次尝试获取权限。", Toast.LENGTH_LONG).show()
						startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
					} else {
						startActivityForResult(
							(getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager).createScreenCaptureIntent(),
							1
						)
					}
				}
				true
			}
		}
		return true
	}

	override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
		Toast.makeText(this, "请求代码${requestCode}的活动结果 = $resultCode", Toast.LENGTH_SHORT).show()
		if (requestCode == 1 && data != null && mMediaProjection == null) {
			val mediaProjection = (getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager).getMediaProjection(resultCode, data)
			mediaProjection.createVirtualDisplay(
				"screen-mirror",
				1920,
				1080,
				Resources.getSystem().getDisplayMetrics().densityDpi,
				DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
				mImageReader.getSurface(), null, null
			)
			mMediaProjection = mediaProjection
		}
	}
}
