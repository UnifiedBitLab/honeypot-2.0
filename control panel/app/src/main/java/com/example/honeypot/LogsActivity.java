package com.example.honeypot;

import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

public class LogsActivity extends AppCompatActivity {
    TextView logsText;
    String BASE_URL = "http://192.168.202.76:5000";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_logs);

        logsText = findViewById(R.id.logsText); // Add a TextView in your layout

        RequestQueue queue = Volley.newRequestQueue(this);
        JsonArrayRequest request = new JsonArrayRequest(Request.Method.GET, BASE_URL + "/logs",
                null,
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
                    logsText.setText(builder.toString());
                },
                error -> logsText.setText("Error loading logs: " + error.getMessage()));
        queue.add(request);
    }
}

