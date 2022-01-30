package io.github.salenzo.myapplication

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.accessibilityservice.GestureDescription.StrokeDescription
import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.graphics.*
import android.graphics.drawable.ColorDrawable
import android.hardware.display.DisplayManager
import android.media.AudioManager
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import android.text.Layout
import android.text.SpannableString
import android.text.TextUtils
import android.text.style.ForegroundColorSpan
import android.text.style.StyleSpan
import android.util.Log
import android.view.*
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.*
import com.chaquo.python.PyException
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.koushikdutta.async.http.body.UrlEncodedFormBody
import com.koushikdutta.async.http.server.AsyncHttpServer
import java.io.File
import java.io.IOException
import java.lang.reflect.Field
import java.net.DatagramSocket
import java.net.InetAddress
import java.nio.ByteBuffer
import java.nio.file.FileVisitResult
import java.nio.file.Files
import java.nio.file.SimpleFileVisitor
import java.nio.file.attribute.BasicFileAttributes
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.FutureTask
import java.util.concurrent.TimeUnit
import kotlin.collections.ArrayDeque
import kotlin.concurrent.thread
import kotlin.io.path.deleteExisting


@SuppressLint("SetTextI18n", "ObsoleteSdkInt")
class InfamousRecidivistService :	AccessibilityService() {
	companion object {
		init {
			System.loadLibrary("myapplication")
	  }
	}

	var mLastKnownRoot: AccessibilityNodeInfo? = null
	var mPythonThread: Thread? = null
	var mPythonThreadId: Long = -1
	var mServer: AsyncHttpServer? = null
	// 被线程安全搞怕了，不敢用数组
	var mtvOutput0: TextView? = null
	var mtvOutput1: TextView? = null
	var mtvOutput2: TextView? = null
	var mtvOutput3: TextView? = null
	var mllTouch: LinearLayout? = null

	@SuppressLint("ClickableViewAccessibility")
	override fun onServiceConnected() {
		// “迫真应用”正在运行
		// 点按即可了解详情或停止应用。
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
			getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel("２５５６５", "迫真传奇重犯正在运行", NotificationManager.IMPORTANCE_DEFAULT))
			startForeground(25565, Notification.Builder(this, "２５５６５").build())
		}

		val wm = getSystemService(WINDOW_SERVICE) as WindowManager
		mllTouch = LinearLayout(this).apply {
			layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.MATCH_PARENT)
			background = ColorDrawable(0x66ccffff)
			addView(ImageView(this@InfamousRecidivistService).apply {
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
				scaleType = ImageView.ScaleType.CENTER_CROP
				setOnTouchListener { view, motionEvent ->
					mtvOutput1?.text = "${motionEvent.rawX}, ${motionEvent.rawY}"
					true
				}
			})
			visibility = ViewGroup.GONE
		}
		wm.addView(mllTouch, WindowManager.LayoutParams(
			WindowManager.LayoutParams.MATCH_PARENT,
			WindowManager.LayoutParams.MATCH_PARENT,
			WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
			WindowManager.LayoutParams.FLAG_FULLSCREEN or WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS or WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
			PixelFormat.TRANSLUCENT
		))
		// Create an overlay and display the action bar
		wm.addView(LinearLayout(this).apply {
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
				text = "View?"
				layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
				setOnClickListener {
					val v = rootInActiveWindow
					if (v != null) {
						//val b = Bitmap.createBitmap(v.width, v.height, Bitmap.Config.ARGB_8888)
						//val c = Canvas(b)
						//v.draw(c)
						//this.background = BitmapDrawable(this@InfamousRecidivistService.resources, b)
						this.text = "${v.viewIdResourceName}\n${v.text}\n${v.hintText}\n${v.windowId}"
						findFocus(AccessibilityNodeInfo.FOCUS_INPUT)?.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, Bundle().apply {
							putString(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, "114514")
						})
					} else {
						this.text = "hengheng"
					}
				}
				//visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "录屏"
				setOnClickListener {
					text = "开始了吗？"
					//background = BitmapDrawable(resources, SelectDeviceActivity.deimg())
				}
				visibility = ViewGroup.GONE
			})
			addView(Button(this@InfamousRecidivistService).apply {
				text = "x, y"
				setOnClickListener {
					if (mllTouch?.visibility == ViewGroup.VISIBLE) {
						mllTouch?.visibility = ViewGroup.GONE
						mtvOutput1?.visibility = ViewGroup.GONE
					} else {
						mllTouch?.visibility = ViewGroup.VISIBLE
						mtvOutput1?.visibility = ViewGroup.VISIBLE
					}
				}
			})
		}, WindowManager.LayoutParams(
			WindowManager.LayoutParams.WRAP_CONTENT,
			WindowManager.LayoutParams.WRAP_CONTENT,
			WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
			WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
			PixelFormat.TRANSLUCENT
		).apply {
			gravity = Gravity.TOP
		})
		wm.addView(LinearLayout(this).apply {
			layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT)
			orientation = LinearLayout.VERTICAL
			addView(TextView(this@InfamousRecidivistService).apply {
				mtvOutput0 = this
				background = ColorDrawable(0x80000000.toInt())
				setTextColor(Color.WHITE)
			})
			addView(TextView(this@InfamousRecidivistService).apply {
				mtvOutput1 = this
				background = ColorDrawable(0x80ffa500.toInt())
				setTextColor(Color.BLACK)
				visibility = ViewGroup.GONE
			})
			addView(TextView(this@InfamousRecidivistService).apply {
				mtvOutput2 = this
				background = ColorDrawable(0xaa114514.toInt())
				setTextColor(Color.WHITE)
				visibility = ViewGroup.GONE
			})
			addView(TextView(this@InfamousRecidivistService).apply {
				mtvOutput3 = this
				background = ColorDrawable(0x89abcdef.toInt())
				setTextColor(Color.BLACK)
				visibility = ViewGroup.GONE
			})
			listOf(mtvOutput0, mtvOutput1, mtvOutput2, mtvOutput3).forEach {
				with(it!!) {
					freezesText = true
					isSingleLine = true
					breakStrategy = Layout.BREAK_STRATEGY_SIMPLE
					ellipsize = TextUtils.TruncateAt.MIDDLE
					typeface = Typeface.MONOSPACE
					setPadding(20, 4, 20, 4)
				}
			}
		}, WindowManager.LayoutParams(
			WindowManager.LayoutParams.MATCH_PARENT,
			WindowManager.LayoutParams.WRAP_CONTENT,
			WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
			WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
			PixelFormat.TRANSLUCENT
		).apply {
			gravity = Gravity.BOTTOM
		})

		val codeDir = File(filesDir, "py")
		codeDir.mkdir()
		val f = File(codeDir, "app.py")
		if (!f.exists()) f.writeText("import infamous_recidivist_service as adb\n\n")
		startPython()
		mServer = AsyncHttpServer().apply {
			val htmlHeader = "<!DOCTYPE html>\n" +
				"<title>Mansfield</title><meta charset=utf-8>\n" +
				"<meta name=viewport content='width=device-width,initial-scale=1,viewport-fit=cover'>\n" +
				"<meta http-equiv=X-UA-Compatible content='IE=edge'>\n"
			// 路由地址参数是自带一个^锚定字符串开头的正则表达式。
			this.get("/") { request, response ->
				response.send(htmlHeader +
					"<style>*{margin:0;padding:0}textarea{width:90vw;height:90vh}</style><center>" +
					"<form method=post><input name=filename value=app.py><input type=submit>\n" +
					"<a href=reload>再运行</a>\n" +
					"<a href=reset title=将会删除提交的所有文件，只留下空的app.py。 onclick=confirm(title)||event.preventDefault()>删光</a>" +
					"<textarea name=contents>" +
					f.readText().replace("&", "&amp;").replace("<", "&lt;")
				)
			}
			this.post("/") { request, response ->
				response.send(htmlHeader +
					"<a href=.>返回</a><p style=white-space:pre>成功" + try {
						val map = request.getBody<UrlEncodedFormBody>().get()
						val filename = map["filename"]!![0]
						val contents = map["contents"]?.get(0)?.toByteArray() ?: Base64.getDecoder().decode(map["base64"]!![0])
						val file = File(codeDir, filename)
						if (!file.canonicalFile.startsWith(codeDir.canonicalFile)) {
							throw SecurityException("你想从这py文件夹逃出去？")
						}
						file.parentFile!!.mkdirs()
						file.writeBytes(contents)
						"了！"
					} catch (e: Exception) {
						response.code(500)
						"搞出" + e.toString() + "\n\n" + f.readText()
					}.replace("&", "&amp;").replace("<", "&lt;")
				)
			}
			this.get("/reload") { request, response ->
				stopPython()
				startPython()
				response.send(htmlHeader +
					"<a href=..>成了！</a>")
			}
			this.get("/reset") { request, response ->
				Files.walkFileTree(codeDir.toPath(), object : SimpleFileVisitor<java.nio.file.Path>() {
					override fun visitFile(file: java.nio.file.Path, attrs: BasicFileAttributes?): FileVisitResult {
						Files.delete(file)
						return FileVisitResult.CONTINUE
					}
					override fun postVisitDirectory(dir: java.nio.file.Path, e: IOException?): FileVisitResult {
						e?.let { throw it }
						dir.deleteExisting()
						return FileVisitResult.CONTINUE
					}
				})
				codeDir.mkdir()
				f.writeText("import infamous_recidivist_service as adb\n\n# ...as you should have known.")
				stopPython()
				response.send("<!DOCTYPE html>\n<title>Breaking news</title>" +
					"<a href=..>呜呼……</a>")
			}
			listen(11451)
		}
		thread {
			DatagramSocket().use {
				it.connect(InetAddress.getByName("8.8.8.114"), 1919)
				log("不言自明：http://${it.localAddress.hostAddress}:11451/。", 16)
			}
		}
	}

	override fun onDestroy() {
		stopPython()
		Log.d("io.salenzo.myapplication - InfamousRecidivist", "onDestroy")
		stopForeground(true)
		mServer?.stop()
	}

	private fun stopPython() {
		try {
			Python.getInstance().getModule("pymain").callAttr("kill_thread", mPythonThreadId)
		} catch (_: PyException) {
		}
		try {
			mPythonThread?.join()
		} catch (_: InterruptedException) {
		}
		mPythonThread = null
	}

	private fun startPython() {
		mPythonThread = thread {
			mPythonThreadId = Python.getInstance().getModule("threading").callAttr("get_ident").toLong()
			Python.getInstance().getModule("pymain").callAttr("main", this@InfamousRecidivistService)
		}
	}

	// dispatchGesture方法元初之时，滑动路径是以100毫秒为周期采样的。
	// 为了解决Android 11才解决的AccessibilityService#dispatchGesture卡顿问题，我直接重写这个方法！
	// 反射，嘿嘿，我的猴子补丁……
	// 当然override是不可能override的，只有自己新建一个方法这样子。
	var mGestureStatusCallbackSequence = 0
	fun anotherDispatchGesture(gesture: GestureDescription): Boolean {
		// 如果是Android 11及以上，就不用自己整了。
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
			return dispatchGesture(gesture, null, null)
		}
		// val connection: IAccessibilityServiceConnection = AccessibilityInteractionClient.getInstance().getConnection(mConnectionId) ?: return false
		val mConnectionId = this.javaClass.superclass.getDeclaredField("mConnectionId").let {
			it.isAccessible = true
			it.get(this) as Int
		}
		val connection = Class.forName("android.view.accessibility.AccessibilityInteractionClient").let {
			it.getMethod("getConnection", Int::class.java).invoke(
				it.getMethod("getInstance").invoke(null),
				mConnectionId
			)
		} ?: return false
		// 但是这个与屏幕刷新率相关的采样率计算方式是Android 12才引入的。
		// 抱歉了，Android 11用户……我就是。哦，我不是高刷新率屏用户啊，那没事了。
		// 为了多显示器支持，需要GestureDescription提供getDisplayId方法，老版本没这支持。
		val sampleTimeMs = (1000 / getSystemService(DisplayManager::class.java).getDisplay(Display.DEFAULT_DISPLAY).refreshRate).toInt()
		// val steps: List<GestureDescription.GestureStep> = MotionEventGenerator.getGestureStepsFromGestureDescription(gesture, sampleTimeMs)
		val steps = Class.forName("android.accessibilityservice.GestureDescription\$MotionEventGenerator")
			.getMethod("getGestureStepsFromGestureDescription", GestureDescription::class.java, Int::class.java)
			.invoke(null, gesture, sampleTimeMs)
		// connection.sendGesture(mGestureStatusCallbackSequence++, ParceledListSlice(steps))
		val classParceledListSlice = Class.forName("android.content.pm.ParceledListSlice")
		Class.forName("android.accessibilityservice.IAccessibilityServiceConnection")
			.getMethod("sendGesture", Int::class.java, classParceledListSlice).invoke(
				connection,
				mGestureStatusCallbackSequence++,
				classParceledListSlice.getConstructor(java.util.List::class.java).newInstance(steps)
			)
		return true
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun swipe(x1: Float, y1: Float, x2: Float, y2: Float, duration: Float) {
		anotherDispatchGesture(GestureDescription.Builder().addStroke(StrokeDescription(Path().apply {
			moveTo(x1, y1)
			lineTo(x2, y2)
		}, 0, (duration * 1000).toLong())).build())
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun tap(x: Float, y: Float) {
		swipe(x - 1, y - 1, x + 1, y + 1, 0.02f)
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun action(action: Int) {
		performGlobalAction(action)
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun screenshot(): PyObject? {
		return when (1) {
			1 -> {
				SelectDeviceActivity.mMediaProjection?.let {
					SelectDeviceActivity.mImageReader.acquireLatestImage()?.let { img ->
						val plane = img.planes[0]
						val rowPadding = plane.rowStride - plane.pixelStride * img.width
						val b = Bitmap.createBitmap(
							img.width + rowPadding / plane.pixelStride, img.height,
							Bitmap.Config.ARGB_8888
						)
						b.copyPixelsFromBuffer(plane.buffer)
						img.close()
						b
					}
				}
			}
			2 -> {
				// 主线程里调用这个会不会死锁啊？
				// FutureTask#get能阻塞，也不知道get了啥。
				val fu = FutureTask {}
				var b: Bitmap? = null
				takeScreenshot(Display.DEFAULT_DISPLAY, mainExecutor, object : TakeScreenshotCallback {
					override fun onSuccess(screenshot: ScreenshotResult) {
						val hb = Bitmap.wrapHardwareBuffer(screenshot.hardwareBuffer, screenshot.colorSpace)!!
						screenshot.hardwareBuffer.close()
						b = hb.copy(Bitmap.Config.ARGB_8888, false)
						fu.run()
					}
					override fun onFailure(errorCode: Int) {
						fu.run()
					}
				})
				fu.get(5, TimeUnit.SECONDS)
				b
			}
			else -> null
		}?.let {
			val w = it.width
			val h = it.height
			val byteBuffer: ByteBuffer = ByteBuffer.allocate(it.rowBytes * h)
			it.copyPixelsToBuffer(byteBuffer)
			it.recycle()
			Python.getInstance().getModule("pymain").callAttr("convert_jarray_to_cv2", byteBuffer.array(), w, h)
		}
	}

	fun log(s: String, style: Int) {
		val styleSpan = when (style) {
			0 -> StyleSpan(Typeface.BOLD_ITALIC) // stdin
			2 -> ForegroundColorSpan(0xffffa500.toInt()) // stderr
			16 -> StyleSpan(Typeface.BOLD) // Java
			else -> StyleSpan(Typeface.NORMAL)
		}
		val ss = SimpleDateFormat("HH:mm:ss ").format(Date()) + if (s.last() != '\n') s + "\n" else s
		mtvOutput0?.post {
			mtvOutput0?.text = SpannableString(ss).apply { setSpan(styleSpan, 8, ss.length, 0) }
		}
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun log(s: PyObject) {
		log(s.toString(), 1)
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun imshow(name: String, mat: PyObject) {
		val shape = mat["shape"]!!.asList()
		val bitmap = Bitmap.createBitmap(
			shape[1].toInt(), shape[0].toInt(),
			Bitmap.Config.ARGB_8888
		)
		val buffer = Python.getInstance().getModule("pymain").callAttr("convert_cv2_to_1darray", mat).toJava(ByteArray::class.java)
		bitmap.copyPixelsFromBuffer(ByteBuffer.wrap(buffer))
		mtvOutput0?.post {
			(mllTouch?.getChildAt(0) as ImageView?)?.setImageBitmap(bitmap)
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

	external fun moretest(): String

	fun testtt() {
		log("114 -> ${moretest()}", 1)
		val f2: Field = this.javaClass.superclass.getField("ACCESSIBILITY_TAKE_SCREENSHOT_REQUEST_INTERVAL_TIMES_MS")
		f2.isAccessible = true
		f2.set(null, 1)
		//val o3 = m3.invoke(null, Class.forName("android.hardware.display.DisplayManagerInternal"))
		if (Build.VERSION.SDK_INT >= 31) {
			val m8 = SurfaceControl::class.java.getMethod("createDisplay", String::class.java, Boolean::class.java)
			val o4 = m8.invoke(null, "scrcpy", false)
			val c2 = Class.forName("android.view.SurfaceControl\$DisplayCaptureArgs")
			val c3 = Class.forName("android.view.SurfaceControl\$DisplayCaptureArgs\$Builder")
			val m5 = c3.getConstructor(IBinder::class.java)
			val m6 = c3.getMethod("setSize", Int::class.java, Int::class.java)
			val m7 = c3.getMethod("build")
			val o5 = m7.invoke(m6.invoke(m5.newInstance(o4), 1920, 1080))
			val m4 = SurfaceControl::class.java.getMethod("captureDisplay", c2)
			val o6 = m4.invoke(null, o5)
			log(">${o6.javaClass.name}", 1)
		} else {
			val m4 = SurfaceControl::class.java.getMethod("screenshot", Rect::class.java, Int::class.java, Int::class.java, Boolean::class.java, Int::class.java)
			val o6 = m4.invoke(null, Rect(), 1920, 1080, false, Surface.ROTATION_0)
			log("<${o6.javaClass.name}", 1)
		}
	}
}
