package io.github.salenzo.myapplication;

import android.app.Application;
import android.content.Context;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import me.weishu.reflection.Reflection;

// Magic starts somewhere.
public class MyApplication extends Application {
	@Override
	public void onCreate() {
		super.onCreate();
		Python.start(new AndroidPlatform(this));
	}

	@Override
	protected void attachBaseContext(Context base) {
		super.attachBaseContext(base);
		Reflection.unseal(base);
	}
}
