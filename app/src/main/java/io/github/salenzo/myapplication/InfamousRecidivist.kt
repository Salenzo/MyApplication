package io.github.salenzo.myapplication

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.accessibilityservice.GestureDescription.StrokeDescription
import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.graphics.Color
import android.graphics.Path
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.ColorDrawable
import android.media.AudioManager
import android.os.Build
import android.text.*
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
import java.net.DatagramSocket
import java.net.InetAddress
import java.nio.ByteBuffer
import java.nio.file.FileVisitResult
import java.nio.file.Files
import java.nio.file.SimpleFileVisitor
import java.nio.file.attribute.BasicFileAttributes
import java.text.SimpleDateFormat
import java.util.*
import kotlin.collections.ArrayDeque
import kotlin.concurrent.thread
import kotlin.io.path.deleteExisting


@SuppressLint("SetTextI18n", "ObsoleteSdkInt")
class InfamousRecidivistService :	AccessibilityService() {
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
			setOnTouchListener { view, motionEvent ->
				mtvOutput1?.text = "${motionEvent.rawX}, ${motionEvent.rawY}"
				true
			}
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
		if (!f.exists()) f.writeBytes(byteArrayOf())
		startPython()
		mServer = AsyncHttpServer().apply {
			val htmlHeader = "<!DOCTYPE html>\n" +
				"<title>Mansfield</title><meta charset=utf-8>\n" +
				"<meta name=viewport content='width=device-width,initial-scale=1,viewport-fit=cover'>\n" +
				"<meta http-equiv=X-UA-Compatible content='IE=edge'>\n"
			// 路由地址参数是自带一个^锚定字符串开头的正则表达式。
			this.get("/") { request, response ->
				response.send(htmlHeader +
					"<style>*{margin:0;padding:0}textarea{border:0;width:99vw;height:99vh}</style>" +
					"<form method=post><input name=filename value=app.py><input type=submit>\n" +
					"<a href=reload>再运行</a>\n" +
					"<a href=reset title=将会删除提交的所有文件，只留下空的app.py。 onclick=if(!confirm(title))event.preventDefault()>删光</a>" +
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
				f.writeBytes(byteArrayOf())
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

	fun swipe(x1: Float, y1: Float, x2: Float, y2: Float, duration: Float) {
		dispatchGesture(GestureDescription.Builder().addStroke(StrokeDescription(Path().apply {
			moveTo(x1, y1)
			lineTo(x2, y2)
		}, 0, (duration * 1000).toLong())).build(), null, null)
	}
	fun tap(x: Float, y: Float) {
		swipe(x - 1, y - 1, x + 1, y + 1, 0.02f)
	}
	fun screenshot(): PyObject? {
		return SelectDeviceActivity.deimg()?.let {
			val byteBuffer: ByteBuffer = ByteBuffer.allocate(it.rowBytes * it.height)
			it.copyPixelsToBuffer(byteBuffer)
			it.recycle()
			Python.getInstance().getModule("pymain").callAttr("convert_jarray_to_cv2", byteBuffer.array(), 1920, 1080)
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
	fun log(s: PyObject) {
		log(s.toString(), 1)
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
