package io.github.salenzo.myapplication;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RemoteViews;

// AbsoluteLayout从API等级3开始就已经弃用了。
// 解决办法是抄一个。因为太啰嗦就把一些没用的功能（内边距、样式等）废掉了。
// 其实厚着脸皮继续用系统提供的废类也完全没问题。或许那个内置类永远也不会再动了，反而是件好事。
@RemoteViews.RemoteView
public class AnotherAbsoluteLayout extends ViewGroup {
	public AnotherAbsoluteLayout(Context context) {
		super(context, null, 0, 0);
	}

	@Override
	protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
		measureChildren(widthMeasureSpec, heightMeasureSpec);

		// Find rightmost and bottom-most child
		int maxHeight = 0;
		int maxWidth = 0;
		int count = getChildCount();
		for (int i = 0; i < count; i++) {
			View child = getChildAt(i);
			if (child.getVisibility() == GONE) continue;
			AnotherAbsoluteLayout.LayoutParams lp = (AnotherAbsoluteLayout.LayoutParams) child.getLayoutParams();
			int childRight = lp.x + child.getMeasuredWidth();
			int childBottom = lp.y + child.getMeasuredHeight();
			maxWidth = Math.max(maxWidth, childRight);
			maxHeight = Math.max(maxHeight, childBottom);
		}

		// Check against minimum height and width.
		setMeasuredDimension(
			resolveSizeAndState(
				Math.max(maxWidth, getSuggestedMinimumWidth()),
				widthMeasureSpec, 0
			),
			resolveSizeAndState(
				Math.max(maxHeight, getSuggestedMinimumHeight()),
				heightMeasureSpec, 0
			)
		);
	}

	@Override
	protected ViewGroup.LayoutParams generateDefaultLayoutParams() {
		return new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT, 0, 0);
	}

	@Override
	protected void onLayout(boolean changed, int l, int t, int r, int b) {
		int count = getChildCount();
		for (int i = 0; i < count; i++) {
			View child = getChildAt(i);
			if (child.getVisibility() == GONE) continue;
			AnotherAbsoluteLayout.LayoutParams lp = (AnotherAbsoluteLayout.LayoutParams) child.getLayoutParams();
			int childLeft = lp.x;
			int childTop = lp.y;
			child.layout(childLeft, childTop,
				childLeft + child.getMeasuredWidth(),
				childTop + child.getMeasuredHeight());
		}
	}

	@Override
	protected boolean checkLayoutParams(ViewGroup.LayoutParams p) {
		return p instanceof AnotherAbsoluteLayout.LayoutParams;
	}

	@Override
	public boolean shouldDelayChildPressedState() {
		return false;
	}

	public static class LayoutParams extends ViewGroup.LayoutParams {
		public int x, y;

		public LayoutParams(int x, int y, int w, int h) {
			super(w, h);
			this.x = x;
			this.y = y;
		}
	}
}
