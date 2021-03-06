package io.github.salenzo.myapplication

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.accessibilityservice.GestureDescription.StrokeDescription
import android.annotation.SuppressLint
import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.graphics.*
import android.graphics.drawable.ColorDrawable
import android.hardware.display.DisplayManager
import android.media.AudioManager
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.net.Uri
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
import java.util.zip.CRC32
import java.util.zip.CheckedInputStream
import kotlin.collections.ArrayDeque
import kotlin.concurrent.thread
import kotlin.io.path.deleteExisting


@SuppressLint("SetTextI18n", "ObsoleteSdkInt")
class InfamousRecidivistService :	AccessibilityService() {
	companion object {
		init {
			System.loadLibrary("myapplication")
	  }
		var mediaProjectionToken: Intent? = null
	}

	lateinit var imageReader: ImageReader
	var mediaProjection: MediaProjection? = null
	fun renewMediaProjection() {
		mediaProjectionToken?.let {
			mediaProjection?.stop()
			mediaProjection = (getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager)
				.getMediaProjection(Activity.RESULT_OK, it.clone() as Intent)
				.also {
					it.createVirtualDisplay(
						"screen-mirror",
						resources.displayMetrics.widthPixels,
						resources.displayMetrics.heightPixels,
						resources.displayMetrics.densityDpi,
						DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
						imageReader.surface, null, null
					)
				}
		}
	}

	var mLastKnownRoot: AccessibilityNodeInfo? = null
	var mPythonThread: Thread? = null
	var mPythonThreadId: Long = -1
	var mServer: AsyncHttpServer? = null
	// ??????????????????????????????????????????
	var mtvOutput0: TextView? = null
	var mtvOutput1: TextView? = null
	var mtvOutput2: TextView? = null
	var mtvOutput3: TextView? = null
	val mtvOutputs: Array<TextView?> = arrayOfNulls(16)
	var mllTouch: LinearLayout? = null

	@SuppressLint("ClickableViewAccessibility")
	override fun onServiceConnected() {
		// ??????????????????????????????
		// ??????????????????????????????????????????
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
			getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel("???????????????", "??????????????????????????????", NotificationManager.IMPORTANCE_DEFAULT))
			startForeground(25565, Notification.Builder(this, "???????????????").build())
		}
		@SuppressLint("WrongConstant") // ????????????????????????????????????????????????????????????
		imageReader = ImageReader.newInstance(
			resources.displayMetrics.widthPixels,
			resources.displayMetrics.heightPixels,
			PixelFormat.RGBA_8888,
			9
		)
		renewMediaProjection()

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
			setOnClickListener {
				PopupMenu(this@InfamousRecidivistService, it, Gravity.BOTTOM).apply {
					menu.add("?????????????????????????????????").setOnMenuItemClickListener {
						(getSystemService(AUDIO_SERVICE) as AudioManager).adjustStreamVolume(
							AudioManager.STREAM_MUSIC,
							AudioManager.ADJUST_RAISE,
							AudioManager.FLAG_SHOW_UI
						)
						true
					}
					menu.add("??????").setOnMenuItemClickListener {
						rootInActiveWindow?.let {
							findScrollableNode(it)?.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD.id)
						} ?: run {
							log("???????????????", 16)
						}
						true
					}
					menu.add("??????").setOnMenuItemClickListener {
						dispatchGesture(GestureDescription.Builder().addStroke(StrokeDescription(Path().apply {
							moveTo(400f, 1000f)
							lineTo(400f, 400f)
						}, 0, 50)).build(), null, null)
						true
					}
					menu.add("??????????????????").setOnMenuItemClickListener {
						val v = rootInActiveWindow
						if (v != null) {
							log("${v.viewIdResourceName}, ${v.text}, ${v.hintText}, ${v.windowId}", 16)
							findFocus(AccessibilityNodeInfo.FOCUS_INPUT)?.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, Bundle().apply {
								putString(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, "114514")
							})
						} else {
							log("hengheng", 16)
						}
						true
					}
					menu.add("???????????????").setOnMenuItemClickListener {
						if (mllTouch?.visibility == ViewGroup.VISIBLE) {
							mllTouch?.visibility = ViewGroup.GONE
							mtvOutput1?.visibility = ViewGroup.GONE
						} else {
							mllTouch?.visibility = ViewGroup.VISIBLE
							mtvOutput1?.visibility = ViewGroup.VISIBLE
						}
						true
					}
					menu.add("??????????????????").setOnMenuItemClickListener {
						if (mediaProjectionToken != null) {
							renewMediaProjection()
						} else {
							GiveMeYourMediaProjectionTokenActivity.fire(this@InfamousRecidivistService)
						}
						true
					}
					menu.add("????????????????????????").setOnMenuItemClickListener {
						startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("http://localhost:11451/")).apply {
							addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
						})
						true
					}
				}.show()
			}
		}, WindowManager.LayoutParams(
			WindowManager.LayoutParams.MATCH_PARENT,
			WindowManager.LayoutParams.WRAP_CONTENT,
			WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
			WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
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
			// ?????????????????????????????????^??????????????????????????????????????????
			this.get("/") { request, response ->
				response.send(htmlHeader +
					"<style>*{margin:0;padding:0}textarea{width:90vw;height:90vh}</style><center>" +
					"<form method=post><input name=filename value=app.py><input type=submit>\n" +
					"<a href=reload>?????????</a>\n" +
					"<a href=reset title=???????????????????????????????????????????????????app.py??? onclick=confirm(title)||event.preventDefault()>??????</a>\n" +
					"<a href=ls title=???????????????????????????ZIP???CRC32???>??????</a>\n" +
					"<div><textarea name=contents>" +
					f.readText().replace("&", "&amp;").replace("<", "&lt;")
				)
			}
			this.post("/") { request, response ->
				response.send(htmlHeader +
					"<a href=.>??????</a><p style=white-space:pre>??????" + try {
						val map = request.getBody<UrlEncodedFormBody>().get()
						val filename = map["filename"]!![0]
						val contents = map["contents"]?.get(0)?.toByteArray() ?: Base64.getDecoder().decode(map["base64"]!![0])
						val file = File(codeDir, filename)
						if (!file.canonicalFile.startsWith(codeDir.canonicalFile)) {
							throw SecurityException("????????????py?????????????????????")
						}
						file.parentFile!!.mkdirs()
						file.writeBytes(contents)
						"??????"
					} catch (e: Exception) {
						response.code(500)
						"??????" + e.toString() + "\n\n" + f.readText()
					}.replace("&", "&amp;").replace("<", "&lt;")
				)
			}
			this.get("/reload") { request, response ->
				stopPython()
				startPython()
				response.send(htmlHeader +
					"<a href=..>?????????</a>")
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
					"<a href=..>????????????</a>")
			}
			this.get("/ls") { request, response ->
				val sb = StringBuilder()
				Files.walkFileTree(codeDir.toPath(), object : SimpleFileVisitor<java.nio.file.Path>() {
					override fun visitFile(file: java.nio.file.Path, attrs: BasicFileAttributes?): FileVisitResult {
						sb.append(codeDir.toPath().relativize(file).toString())
						sb.append('\t')
						sb.append(Files.size(file))
						sb.append(try {
							val cis = CheckedInputStream(file.toFile().inputStream(), CRC32())
							val buf = ByteArray(4096)
							while (cis.read(buf) >= 0) {
								// ?????????????????????IDEA??????????????????
							}
							"\t%08x\n".format(cis.checksum.value)
						} catch (e: IOException) {
							"\tERROR\n"
						})
						return FileVisitResult.CONTINUE
					}
				})
				response.send("text/plain", sb.toString())
			}
			listen(11451)
		}
		thread {
			DatagramSocket().use {
				it.connect(InetAddress.getByName("8.8.8.114"), 1919)
				log("???????????????http://${it.localAddress.hostAddress}:11451/???", 16)
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

	// dispatchGesture???????????????????????????????????????100???????????????????????????
	// ????????????Android 11????????????AccessibilityService#dispatchGesture?????????????????????????????????????????????
	// ??????????????????????????????????????????
	// ??????override????????????override????????????????????????????????????????????????
	var mGestureStatusCallbackSequence = 0
	fun anotherDispatchGesture(gesture: GestureDescription): Boolean {
		// ?????????Android 11????????????????????????????????????
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
		// ???????????????????????????????????????????????????????????????Android 12???????????????
		// ????????????Android 11?????????????????????????????????????????????????????????????????????????????????
		// ?????????????????????????????????GestureDescription??????getDisplayId?????????????????????????????????
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
		// ???Path bounds must not be negative?????????Android????????????????????????????????????
		swipe((x - 1).coerceAtLeast(0f), (y - 1).coerceAtLeast(0f), x + 1, y + 1, 0.02f)
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun action(action: Int) {
		performGlobalAction(action)
	}

	@Suppress("unused", "MemberVisibilityCanBePrivate")
	fun screenshot(): PyObject? {
		return when (1) {
			1 -> {
				imageReader.acquireLatestImage()?.let { img ->
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
			2 -> {
				// ?????????????????????????????????????????????
				// FutureTask#get????????????????????????get?????????
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

	class GiveMeYourMediaProjectionTokenActivity : Activity() {
		override fun onStart() {
			super.onStart()
			startActivityForResult(
				(getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager).createScreenCaptureIntent(),
				1
			)
		}

		override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
			super.onActivityResult(requestCode, resultCode, data)
			Log.i(localClassName, "activity ${requestCode} result = ${resultCode}")
			if (requestCode == 1) {
				if (data != null) mediaProjectionToken = data
				finish()
			}
		}

		companion object {
			fun fire(context: Context) {
				if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) return
				context.startActivity(Intent(context, this::class.java.declaringClass).apply {
					addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_NO_ANIMATION)
				})
			}
		}
	}
}
