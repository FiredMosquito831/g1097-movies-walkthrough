package ro.ase.ie.dma02;

import android.app.Activity;
import android.app.Application;
import android.os.Bundle;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.google.android.material.color.DynamicColors;

public class DMA02App
        extends Application
        implements Application.ActivityLifecycleCallbacks {

    private final String TAG = DMA02App.class.getSimpleName();

    @Override
    public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
        DynamicColors.applyToActivitiesIfAvailable(this);

        Log.w(TAG, "onCreate");
    }

    @Override
    public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
        Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityDestroyed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityDestroyed" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityPaused(@NonNull Activity activity) {
        Log.w(TAG, "onActivityPaused" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityResumed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityResumed" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {

    }

    @Override
    public void onActivityStarted(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStarted" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityStopped(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStopped" + activity.getClass().getSimpleName());
    }
}
