package io.github.salenzo.myapplication

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.accessibilityservice.GestureDescription.StrokeDescription
import android.annotation.SuppressLint
import android.graphics.Path
import android.graphics.PixelFormat
import android.media.AudioManager
import android.view.Gravity
import android.view.ViewGroup
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast


class InfamousRecidivist

@SuppressLint("SetTextI18n")
class InfamousRecidivistService :	AccessibilityService() {
	var mLayout: LinearLayout? = null
	var mLastKnownRoot: AccessibilityNodeInfo? = null

	override fun onServiceConnected() {
		// Create an overlay and display the action bar
		val wm = getSystemService(WINDOW_SERVICE) as WindowManager
		mLayout = LinearLayout(this).apply {
			layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT)
			orientation = LinearLayout.HORIZONTAL
			addView(Button(this@InfamousRecidivistService).apply {
				text = "パワー"
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					performGlobalAction(GLOBAL_ACTION_POWER_DIALOG)
				}
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "发出很大声音程度的能力"
				textSize /= 4
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					(getSystemService(AUDIO_SERVICE) as AudioManager).adjustStreamVolume(
						AudioManager.STREAM_MUSIC,
						AudioManager.ADJUST_RAISE,
						AudioManager.FLAG_SHOW_UI
					)
				}
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
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "swipe"
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					dispatchGesture(GestureDescription.Builder().addStroke(StrokeDescription(Path().apply {
						moveTo(400f, 1000f)
						lineTo(400f, 400f)
					}, 0, 500)).build(), null, null)
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
