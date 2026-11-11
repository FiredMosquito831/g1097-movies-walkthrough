package ro.ase.ie.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

import java.util.List;

import ro.ase.ie.dma06.R;

/** Step 2: fills a two-column row for a ListView. */
public class NumberListAdapter extends BaseAdapter {

    private static class ViewHolder {
        TextView tvDecimal;
        TextView tvBinary;
    }

    private final List<Integer> numbers;
    private final LayoutInflater layoutInflater;

    public NumberListAdapter(Context context, List<Integer> numbers) {
        this.layoutInflater = LayoutInflater.from(context);
        this.numbers = numbers;
    }

    @Override
    public int getCount() {
        return numbers.size();
    }

    @Override
    public Integer getItem(int position) {
        return numbers.get(position);
    }

    @Override
    public long getItemId(int position) {
        // Each number is unique, so the number itself can be the ID
        return numbers.get(position);
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;

        if (convertView == null) {
            // New row: inflate it and store its views
            convertView = layoutInflater.inflate(R.layout.item_number, parent, false);
            holder = new ViewHolder();
            holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);
            holder.tvBinary = convertView.findViewById(R.id.tvBinary);
            convertView.setTag(holder);
        } else {
            // Reused row: get its stored views
            holder = (ViewHolder) convertView.getTag();
        }

        int number = getItem(position);
        holder.tvDecimal.setText(String.valueOf(number));
        holder.tvBinary.setText(Integer.toBinaryString(number));

        return convertView;
    }
}
