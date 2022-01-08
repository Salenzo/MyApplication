package io.github.salenzo.myapplication

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.accessibilityservice.GestureDescription.StrokeDescription
import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.graphics.Path
import android.graphics.PixelFormat
import android.graphics.drawable.BitmapDrawable
import android.media.AudioManager
import android.os.Build
import android.view.Gravity
import android.view.ViewGroup
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import com.chaquo.python.Python
import java.nio.ByteBuffer
import kotlin.concurrent.thread


class InfamousRecidivist

@SuppressLint("SetTextI18n", "ObsoleteSdkInt")
class InfamousRecidivistService :	AccessibilityService() {
	var mLayout: LinearLayout? = null
	var mLastKnownRoot: AccessibilityNodeInfo? = null
	var mPythonThread: Thread? = null
	var mPythonThreadId: Long = -1
	override fun onServiceConnected() {
		// “迫真应用”正在运行
		// 点按即可了解详情或停止应用。
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
			getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel("２５５６５", "迫真传奇重犯正在运行", NotificationManager.IMPORTANCE_DEFAULT))
		}
		startForeground(25565, Notification.Builder(this, "２５５６５").build())

		// Create an overlay and display the action bar
		val wm = getSystemService(WINDOW_SERVICE) as WindowManager
		mLayout = LinearLayout(this).apply {
			layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT)
			orientation = LinearLayout.VERTICAL
			addView(Button(this@InfamousRecidivistService).apply {
				text = "パワー"
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					performGlobalAction(GLOBAL_ACTION_POWER_DIALOG)
				}
				visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "发出很大声音\n程度的能力"
				textSize /= 4
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					(getSystemService(AUDIO_SERVICE) as AudioManager).adjustStreamVolume(
						AudioManager.STREAM_MUSIC,
						AudioManager.ADJUST_RAISE,
						AudioManager.FLAG_SHOW_UI
					)
				}
				visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "scroll"
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					rootInActiveWindow?.let {
						findScrollableNode(it)?.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD.id)
					} ?: run {
						Toast.makeText(this@InfamousRecidivistService, "失敗した…", Toast.LENGTH_SHORT)
					}
				}
				visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "swipe"
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					dispatchGesture(GestureDescription.Builder().addStroke(StrokeDescription(Path().apply {
						moveTo(400f, 1000f)
						lineTo(400f, 400f)
					}, 0, 50)).build(), null, null)
				}
				visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "Python"
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					val x = Python.getInstance().getModule("pymain").callAttr("aaa", "我${BuildConfig.APPLICATION_ID}用的CV版本是").toString()
					Toast.makeText(this@InfamousRecidivistService, x, Toast.LENGTH_SHORT)
					this.text = x
				}
				visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "录屏"
				width = 192
				height = 108
				setOnClickListener {
					text = "开始了吗？"
					background = BitmapDrawable(resources, SelectDeviceActivity.deimg())
				}
				visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "执行"
				setOnClickListener {
					if (text == "执行") {
						mPythonThread = thread {
							mPythonThreadId = Python.getInstance().getModule("threading").callAttr("get_ident").toLong()
							Python.getInstance().getModule("pymain").callAttr("main", this@InfamousRecidivistService)
						}
						text = "赫赫有名之停不下来"
					} else {
						Python.getInstance().getModule("pymain").callAttr("kill_thread", mPythonThreadId)
						text = "执行"
					}
				}
			})
		}
		wm.addView(mLayout, WindowManager.LayoutParams().apply {
			type = WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY
			format = PixelFormat.TRANSLUCENT
			flags = flags or WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
			width = WindowManager.LayoutParams.WRAP_CONTENT
			height = WindowManager.LayoutParams.WRAP_CONTENT
			gravity = Gravity.TOP
		})
	}
	fun swipe(x1: Float, y1: Float, x2: Float, y2: Float, duration: Float) {
		dispatchGesture(GestureDescription.Builder().addStroke(StrokeDescription(Path().apply {
			moveTo(x1, y1)
			lineTo(x2, y2)
		}, 0, (duration * 1000).toLong())).build(), null, null)
	}
	fun tap(x: Float, y: Float) {
		swipe(x - 1, y - 1, x + 1, y + 1, 0.02f)
	}
	fun screenshot(): ByteArray? {
		return SelectDeviceActivity.deimg()?.let {
			val byteBuffer: ByteBuffer = ByteBuffer.allocate(it.getRowBytes() * it.getHeight())
			it.copyPixelsToBuffer(byteBuffer)
			it.recycle()
			byteBuffer.array()
		}
	}
	private fun findScrollableNode(root: AccessibilityNodeInfo): AccessibilityNodeInfo? {
		val deque: ArrayDeque<AccessibilityNodeInfo> = ArrayDeque()
		deque.add(root)
		while (!deque.isEmpty()) {
			val node: AccessibilityNodeInfo = deque.removeFirst()
			if (node.actionList.contains(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD)) {
				return node
			}
			for (i in 0 until node.childCount) {
				deque.addLast(node.getChild(i))
			}
		}
		return null
	}
	override fun onAccessibilityEvent(event: AccessibilityEvent) {
		var root = event.source
		while (root != null) {
			mLastKnownRoot = root
			root = root.parent
		}
	}
	override fun onInterrupt() {

	}
	override fun getRootInActiveWindow(): AccessibilityNodeInfo? {
		return super.getRootInActiveWindow() ?: mLastKnownRoot
	}
}
