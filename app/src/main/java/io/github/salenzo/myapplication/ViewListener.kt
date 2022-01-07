package io.github.salenzo.myapplication

import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothHidDevice
import android.util.Log
import android.view.MotionEvent
import android.view.View
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.roundToInt

class ViewListener(
	val hidDevice: BluetoothHidDevice,
	val host: BluetoothDevice
) : View.OnTouchListener {
	private var previousX = 0f
	private var previousY = 0f
	override fun onTouch(v: View, event: MotionEvent): Boolean {
		val x = event.x
		val y = event.y
		when (event.action) {
			MotionEvent.ACTION_MOVE -> {
				Log.d("pointerCount_is", event.pointerCount.toString())
				if (event.pointerCount == 1) {
					var dxInt: Int = (x - previousX).roundToInt()
					if (dxInt > 2047) dxInt = 2047
					if (dxInt < -2047) dxInt = -2047

					var dyInt: Int = (y - previousY).roundToInt()
					if (dyInt > 2047) dyInt = 2047
					if (dyInt < -2047) dyInt = -2047

					val bytesArrX = ByteArray(7) { 0 }
					val buffX: ByteBuffer = ByteBuffer.wrap(bytesArrX)
					buffX.order(ByteOrder.LITTLE_ENDIAN).put(0).putShort(dxInt.toShort()).putShort(dyInt.toShort()).putShort(0)
					Log.d("ddf2", bytesArrX.contentToString())
					hidDevice.sendReport(this.host, 4, bytesArrX)
				}
			}
			MotionEvent.ACTION_UP -> {
				v.performClick()
				hidDevice.sendReport(this.host, 4, ByteArray(7) {0})
			}
		}
		previousX = x
		previousY = y
		return true
	}
}