package ro.ase.ie.dma06.activities;

import android.os.Bundle;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.adapters.NumberListAdapter;
import ro.ase.ie.data.NumberData;
import ro.ase.ie.dma06.R;


/**
 * Step 2: two columns in a ListView.
 * A custom adapter fills each column of the row layout.
 */
public class TwoColumnActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_two_column);

        ListView lvNumbers = findViewById(R.id.lvNumbers);

        NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
        lvNumbers.setAdapter(adapter);
    }
}
