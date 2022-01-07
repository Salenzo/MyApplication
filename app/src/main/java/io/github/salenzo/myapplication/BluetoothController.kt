package io.github.salenzo.myapplication

import android.annotation.SuppressLint
import android.bluetooth.*
import android.content.Context
import android.graphics.drawable.Drawable
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.util.Log

@Suppress("MemberVisibilityCanBePrivate")
object BluetoothController : BluetoothHidDevice.Callback(), BluetoothProfile.ServiceListener {
	override fun onSetReport(device: BluetoothDevice?, type: Byte, id: Byte, data: ByteArray?) {
		super.onSetReport(device, type, id, data)
		Log.i("$TAG, setreport", "this $device and $type and $id and $data")
	}

	override fun onGetReport(device: BluetoothDevice?, type: Byte, id: Byte, bufferSize: Int) {
		super.onGetReport(device, type, id, bufferSize)
		Log.i("$TAG, get", "second")
		if (type == BluetoothHidDevice.REPORT_TYPE_FEATURE) {
			Log.i("$TAG, getbthid", "$btHid")

			// bit 0 = wheelResolutionMultiplier
			// bit 2 = acPanResolutionMultiplier
			val wasrs = btHid?.replyReport(device, type, 6, byteArrayOf(0x05))
			Log.i("$TAG, replysuccess flag", wasrs.toString())
		}
	}

	val btAdapter by lazy { BluetoothAdapter.getDefaultAdapter()!! }
	var btHid: BluetoothHidDevice? = null
	var hostDevice: BluetoothDevice? = null

	var deviceListener: ((BluetoothHidDevice, BluetoothDevice) -> Unit)? = null
	var disconnectListener: (() -> Unit)? = null

	fun init(context: Context) {
		Log.i(TAG, "init")
		if (btHid != null) {
			Log.i(TAG, "already inited")
			return
		}
		btAdapter.getProfileProxy(context, this, BluetoothProfile.HID_DEVICE)
	}

	fun getSender(callback: (BluetoothHidDevice, BluetoothDevice) -> Unit) {
		Log.i(TAG, "getting sender")
		btHid?.let { hidd ->
			hostDevice?.let { host ->
				callback(hidd, host)
				return
			}
		}
		deviceListener = callback
	}

	override fun onServiceConnected(profile: Int, proxy: BluetoothProfile) {
		Log.i(TAG, "Connected to service")
		this.btHid = proxy as BluetoothHidDevice
		proxy.registerApp(
			BluetoothHidDeviceAppSdpSettings(
				// 50 bytes max.
				"Will the name ever be displayed?",
				"Will the description ever be displayed?",
				"Will the provider ever be displayed?",
				BluetoothHidDevice.SUBCLASS1_COMBO,
				byteArrayOf(
					//MOUSE TLC
					0x05.toByte(), 0x01.toByte(),                         // USAGE_PAGE (Generic Desktop)
					0x09.toByte(), 0x02.toByte(),                         // USAGE (Mouse)

					0xa1.toByte(), 0x01.toByte(),                         // COLLECTION (Application)
					0x05.toByte(), 0x01.toByte(),                         // USAGE_PAGE (Generic Desktop)
					0x09.toByte(), 0x02.toByte(),                         // USAGE (Mouse)
					0xa1.toByte(), 0x02.toByte(),        //       COLLECTION (Logical)

					0x85.toByte(), 0x04.toByte(),               //   REPORT_ID (Mouse)
					0x09.toByte(), 0x01.toByte(),                         //   USAGE (Pointer)
					0xa1.toByte(), 0x00.toByte(),                         //   COLLECTION (Physical)
					0x05.toByte(), 0x09.toByte(),                         //     USAGE_PAGE (Button)
					0x19.toByte(), 0x01.toByte(),                         //     USAGE_MINIMUM (Button 1)
					0x29.toByte(), 0x02.toByte(),                         //     USAGE_MAXIMUM (Button 2)
					0x15.toByte(), 0x00.toByte(),                         //     LOGICAL_MINIMUM (0)
					0x25.toByte(), 0x01.toByte(),                         //     LOGICAL_MAXIMUM (1)
					0x75.toByte(), 0x01.toByte(),                         //     REPORT_SIZE (1)
					0x95.toByte(), 0x02.toByte(),                         //     REPORT_COUNT (2)
					0x81.toByte(), 0x02.toByte(),                         //     INPUT (Data,Var,Abs)
					0x95.toByte(), 0x01.toByte(),                         //     REPORT_COUNT (1)
					0x75.toByte(), 0x06.toByte(),                         //     REPORT_SIZE (6)
					0x81.toByte(), 0x03.toByte(),                         //     INPUT (Cnst,Var,Abs)
					0x05.toByte(), 0x01.toByte(),                         //     USAGE_PAGE (Generic Desktop)
					0x09.toByte(), 0x30.toByte(),                         //     USAGE (X)
					0x09.toByte(), 0x31.toByte(),                         //     USAGE (Y)
					0x16.toByte(), 0x01.toByte(), 0xf8.toByte(),                         //     LOGICAL_MINIMUM (-2047)
					0x26.toByte(), 0xff.toByte(), 0x07.toByte(),                         //     LOGICAL_MAXIMUM (2047)
					0x75.toByte(), 0x10.toByte(),                         //     REPORT_SIZE (16)
					0x95.toByte(), 0x02.toByte(),                         //     REPORT_COUNT (2)
					0x81.toByte(), 0x06.toByte(),                         //     INPUT (Data,Var,Rel)

					0xa1.toByte(), 0x02.toByte(),        //       COLLECTION (Logical)
					0x85.toByte(), 0x06.toByte(),               //   REPORT_ID (Feature)
					0x09.toByte(), 0x48.toByte(),        //         USAGE (Resolution Multiplier)

					0x15.toByte(), 0x00.toByte(),        //         LOGICAL_MINIMUM (0)
					0x25.toByte(), 0x01.toByte(),        //         LOGICAL_MAXIMUM (1)
					0x35.toByte(), 0x01.toByte(),        //         PHYSICAL_MINIMUM (1)
					0x45.toByte(), 0x04.toByte(),        //         PHYSICAL_MAXIMUM (4)
					0x75.toByte(), 0x02.toByte(),        //         REPORT_SIZE (2)
					0x95.toByte(), 0x01.toByte(),        //         REPORT_COUNT (1)

					0xb1.toByte(), 0x02.toByte(),        //         FEATURE (Data,Var,Abs)


					0x85.toByte(), 0x04.toByte(),               //   REPORT_ID (Mouse)
					//0x05.toByte(), 0x01.toByte(),                         //     USAGE_PAGE (Generic Desktop)
					0x09.toByte(), 0x38.toByte(),        //         USAGE (Wheel)

					0x15.toByte(), 0x81.toByte(),        //         LOGICAL_MINIMUM (-127)
					0x25.toByte(), 0x7f.toByte(),        //         LOGICAL_MAXIMUM (127)
					0x35.toByte(), 0x00.toByte(),        //         PHYSICAL_MINIMUM (0)        - reset physical
					0x45.toByte(), 0x00.toByte(),        //         PHYSICAL_MAXIMUM (0)
					0x75.toByte(), 0x08.toByte(),        //         REPORT_SIZE (8)
					0x95.toByte(), 0x01.toByte(),                         //     REPORT_COUNT (1)
					0x81.toByte(), 0x06.toByte(),                         //     INPUT (Data,Var,Rel)
					0xc0.toByte(),              //       END_COLLECTION

					0xa1.toByte(), 0x02.toByte(),        //       COLLECTION (Logical)
					0x85.toByte(), 0x06.toByte(),               //   REPORT_ID (Feature)
					0x09.toByte(), 0x48.toByte(),        //         USAGE (Resolution Multiplier)

					0x15.toByte(), 0x00.toByte(),        //         LOGICAL_MINIMUM (0)
					0x25.toByte(), 0x01.toByte(),        //         LOGICAL_MAXIMUM (1)
					0x35.toByte(), 0x01.toByte(),        //         PHYSICAL_MINIMUM (1)
					0x45.toByte(), 0x04.toByte(),        //         PHYSICAL_MAXIMUM (4)
					0x75.toByte(), 0x02.toByte(),        //         REPORT_SIZE (2)
					0x95.toByte(), 0x01.toByte(),        //         REPORT_COUNT (1)

					0xb1.toByte(), 0x02.toByte(),        //         FEATURE (Data,Var,Abs)

					0x35.toByte(), 0x00.toByte(),        //         PHYSICAL_MINIMUM (0)        - reset physical
					0x45.toByte(), 0x00.toByte(),        //         PHYSICAL_MAXIMUM (0)
					0x75.toByte(), 0x04.toByte(),        //         REPORT_SIZE (4)
					0xb1.toByte(), 0x03.toByte(),        //         FEATURE (Cnst,Var,Abs)


					0x85.toByte(), 0x04.toByte(),               //   REPORT_ID (Mouse)
					0x05.toByte(), 0x0c.toByte(),        //         USAGE_PAGE (Consumer Devices)
					0x0a.toByte(), 0x38.toByte(), 0x02.toByte(),  //         USAGE (AC Pan)

					0x15.toByte(), 0x81.toByte(),        //         LOGICAL_MINIMUM (-127)
					0x25.toByte(), 0x7f.toByte(),        //         LOGICAL_MAXIMUM (127)
					0x75.toByte(), 0x08.toByte(),        //         REPORT_SIZE (8)
					0x95.toByte(), 0x01.toByte(),        //         REPORT_COUNT (1)
					0x81.toByte(), 0x06.toByte(),        //         INPUT (Data,Var,Rel)
					0xc0.toByte(),              //       END_COLLECTION
					0xc0.toByte(),              //       END_COLLECTION

					0xc0.toByte(),                               //   END_COLLECTION
					0xc0.toByte(),                                //END_COLLECTION

					0x05.toByte(), 0x01.toByte(),                         // USAGE_PAGE (Generic Desktop)

					0x09.toByte(), 0x06.toByte(),                         // Usage (Keyboard)
					0xA1.toByte(), 0x01.toByte(),                         // Collection (Application)
					0x85.toByte(), 0x08.toByte(),                           //   REPORT_ID (Keyboard)
					0x05.toByte(), 0x07.toByte(),                         //     Usage Page (Key Codes)
					0x19.toByte(), 0xe0.toByte(),                         //     Usage Minimum (224)
					0x29.toByte(), 0xe7.toByte(),                         //     Usage Maximum (231)
					0x15.toByte(), 0x00.toByte(),                         //     Logical Minimum (0)
					0x25.toByte(), 0x01.toByte(),                         //     Logical Maximum (1)
					0x75.toByte(), 0x01.toByte(),                         //     Report Size (1)
					0x95.toByte(), 0x08.toByte(),                         //     Report Count (8)
					0x81.toByte(), 0x02.toByte(),                         //     Input (Data, Variable, Absolute)

					0x95.toByte(), 0x01.toByte(),                         //     Report Count (1)
					0x75.toByte(), 0x08.toByte(),                         //     Report Size (8)
					0x81.toByte(), 0x01.toByte(),                         //     Input (Constant) reserved byte(1)

					0x95.toByte(), 0x01.toByte(),                         //     Report Count (1)
					0x75.toByte(), 0x08.toByte(),                         //     Report Size (8)
					0x15.toByte(), 0x00.toByte(),                         //     Logical Minimum (0)
					0x25.toByte(), 0x65.toByte(),                         //     Logical Maximum (101)
					0x05.toByte(), 0x07.toByte(),                         //     Usage Page (Key codes)
					0x19.toByte(), 0x00.toByte(),                         //     Usage Minimum (0)
					0x29.toByte(), 0x65.toByte(),                         //     Usage Maximum (101)
					0x81.toByte(), 0x00.toByte(),                         //     Input (Data, Array) Key array(6 bytes)
					0xc0.toByte()                               // End Collection (Application)
				)
			),
			null,
			BluetoothHidDeviceAppQosSettings(
				BluetoothHidDeviceAppQosSettings.SERVICE_BEST_EFFORT,
				800,
				9,
				0,
				11250,
				BluetoothHidDeviceAppQosSettings.MAX
			),
			{ it.run() },
			this
		)
	}

	override fun onServiceDisconnected(profile: Int) {
		Log.e(TAG, "Service disconnected!")
		btHid = null
	}

	override fun onAppStatusChanged(pluggedDevice: BluetoothDevice?, registered: Boolean) {
		super.onAppStatusChanged(pluggedDevice, registered)
		Log.d(TAG, "onAppStatusChanged: pluggedDevice=$pluggedDevice registered=$registered")
	}

	override fun onConnectionStateChanged(device: BluetoothDevice?, state: Int) {
		super.onConnectionStateChanged(device, state)
		Log.i(TAG, "Connection state ${state}")
		if (state == BluetoothProfile.STATE_CONNECTED) {
			if (device != null) {
				hostDevice = device
				deviceListener?.invoke(btHid!!, device)
				Log.e(TAG, "Device connected")
			} else {
				Log.e(TAG, "Device not connected")
			}
		} else {
			hostDevice = null
			if (state == BluetoothProfile.STATE_DISCONNECTED) {
				Log.i(TAG, "Disconnected")
				disconnectListener?.invoke()
			}
		}
	}

	const val TAG = "BluetoothController"
}

object MyCompatibility {
	@SuppressLint("ObsoleteSdkInt")
	fun viberate(context: Context, milliseconds: Long) {
		val v = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
			v.vibrate(VibrationEffect.createOneShot(milliseconds, 240)) // 1 ~ 255
		} else {
			v.vibrate(milliseconds)
		}
	}

	@SuppressLint("ObsoleteSdkInt")
	fun getDrawable(context: Context, id: Int): Drawable {
		return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
			context.getDrawable(id)!!
		} else {
			context.resources.getDrawable(id)
		}
	}
}
