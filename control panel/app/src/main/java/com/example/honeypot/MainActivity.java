package com.example.honeypot;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    TextView outputText;
    String BASE_URL = "http://192.168.202.76:5000";
    RequestQueue requestQueue;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        outputText = findViewById(R.id.outputText);
        requestQueue = Volley.newRequestQueue(this);

        CardView cardStart = findViewById(R.id.cardStart);
        CardView cardStop = findViewById(R.id.cardStop);
        CardView cardStatus = findViewById(R.id.cardStatus);
        CardView cardLogs = findViewById(R.id.cardLogs);

        cardStart.setOnClickListener(view -> sendRequest("/start", Request.Method.POST, view));
        cardStop.setOnClickListener(view -> sendRequest("/stop", Request.Method.POST, view));
        cardStatus.setOnClickListener(view -> sendRequest("/status", Request.Method.GET, view));

        cardLogs.setOnClickListener(v ->
                startActivity(new Intent(this, LogsActivity.class))
        );

    }

    private void sendRequest(String endpoint, int method, View clickedView) {
        clickedView.setEnabled(false);
        String url = BASE_URL + endpoint;

        JsonObjectRequest request = new JsonObjectRequest(method, url, null,
                response -> {
                    try {
                        String status = response.getString("status");
                        String output = response.has("output") ? response.getString("output") : "";
                        String message = "Status: " + status + "\nOutput:\n" + output;
                        outputText.setText(message);
                        Log.d("VolleyResponse", message);
                    } catch (JSONException e) {
                        outputText.setText("JSON parsing error: " + e.getMessage());
                    }
                    clickedView.setEnabled(true);
                },
                error -> {
                    outputText.setText("Volley error: " + error.toString());
                    clickedView.setEnabled(true);
                });

        request.setRetryPolicy(new com.android.volley.DefaultRetryPolicy(
                3000,
                0,
                com.android.volley.DefaultRetryPolicy.DEFAULT_BACKOFF_MULT
        ));

        requestQueue.add(request);
    }
}
