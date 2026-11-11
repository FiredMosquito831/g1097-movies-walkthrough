package ro.ase.ie.dma06.activities;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.DividerItemDecoration;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.adapters.NumberRecyclerAdapter;
import ro.ase.ie.data.NumberData;
import ro.ase.ie.dma06.R;


/**
 * Step 3: the same two columns in a RecyclerView.
 * RecyclerView needs a LayoutManager, and dividers are added separately.
 */
public class RecyclerViewActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_recycler_view);

        RecyclerView rvNumbers = findViewById(R.id.rvNumbers);

        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        rvNumbers.setLayoutManager(layoutManager);
        rvNumbers.addItemDecoration(
                new DividerItemDecoration(this, layoutManager.getOrientation()));

        NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
        rvNumbers.setAdapter(adapter);
    }
}
