package com.example.honeypot;

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

public class FilterLogsActivity extends AppCompatActivity {
    EditText filterInput;
    Button btnFilter;
    TextView filterResult;
    String BASE_URL = "http://192.168.202.76:5000";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_filter_logs);

        filterInput = findViewById(R.id.filterInput);
        btnFilter = findViewById(R.id.btnFilter);
        filterResult = findViewById(R.id.filterResult);

        btnFilter.setOnClickListener(v -> {
            String keyword = filterInput.getText().toString().trim();
            try {
                JSONObject payload = new JSONObject();
                payload.put("keyword", keyword);

                RequestQueue queue = Volley.newRequestQueue(this);
                JsonArrayRequest request = new JsonArrayRequest(Request.Method.POST,
                        BASE_URL + "/filter",
                        payload.names(),
                        response -> {
                            StringBuilder builder = new StringBuilder();
                            for (int i = 0; i < response.length(); i++) {
                                try {
                                    JSONObject log = response.getJSONObject(i);
                                    builder.append(log.toString()).append("\n\n");
                                } catch (JSONException e) {
                                    e.printStackTrace();
                                }
                            }
                            filterResult.setText(builder.toString());
                        },
                        error -> filterResult.setText("Error: " + error.getMessage()));
                queue.add(request);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        });
    }
}
