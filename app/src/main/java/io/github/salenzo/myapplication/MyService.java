package io.github.salenzo.myapplication;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;

public class MyService extends Service {
	public Thread myThread;
	public MyService() {
	}

	@Override
	public void onCreate() {
		super.onCreate();
		Log.d("Bluetooth MyService", "onCreate called!");
	}

	@Override
	public IBinder onBind(Intent intent) {
		return null;
	}

	@Override
	public int onStartCommand(Intent intent, int flags, int startId) {
		super.onStartCommand(intent, flags, startId);
		Log.d("Bluetooth MyService", "onStart called!");
		if (myThread != null) {
			Log.d("Bluetooth MyService", "Already myThread!");
		} else {
			myThread = (new Thread(() -> {
				Log.d("Bluetooth MyService", "Inside thread!");
				try {
					Thread.sleep(1145);
				} catch (InterruptedException ignored) {
				}
				Log.d("Bluetooth MyService", "Inside thread!");
			}, "Bluetooth MyService thread"));
			myThread.start();
		}
		return START_STICKY;
	}

	@Override
	public void onDestroy() {
		super.onDestroy();
		Log.d("Bluetooth MyService", "onDestroy called!");
		myThread.interrupt();
	}
}
