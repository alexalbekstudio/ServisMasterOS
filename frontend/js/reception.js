document.addEventListener("DOMContentLoaded", async () => {
    // Elementi forme
    const customerSearch = document.getElementById("customer-search");
    const customerResults = document.getElementById("customer-results");
    const selectedCustomerId = document.getElementById("selected-customer-id");
    const newCustomerName = document.getElementById("new-customer-name");
    const newCustomerPhone = document.getElementById("new-customer-phone");
    const newCustomerFields = document.getElementById("new-customer-fields");

    const vehiclePlate = document.getElementById("vehicle-plate");
    const vehicleResults = document.getElementById("vehicle-results");
    const selectedVehicleId = document.getElementById("selected-vehicle-id");
    const vehicleMake = document.getElementById("vehicle-make");
    const vehicleModel = document.getElementById("vehicle-model");
    const vehicleVin = document.getElementById("vehicle-vin");

    const historyContainer = document.getElementById("vehicle-history-container");
    const historyList = document.getElementById("history-items-list");
    const historyVisitsCount = document.getElementById("history-visits-count");

    // OCR i Kamera
    const btnOpenLiveCam = document.getElementById("btn-open-live-cam");
    const btnTriggerFileUpload = document.getElementById("btn-trigger-file-upload");
    const ocrFileInput = document.getElementById("ocr-file-input");
    const cameraModal = document.getElementById("camera-modal");
    const cameraVideo = document.getElementById("camera-video");
    const btnCloseCam = document.getElementById("btn-close-camera");
    const btnTakeSnapshot = document.getElementById("btn-take-snapshot");
    const cameraCanvas = document.getElementById("camera-canvas");
    const ocrProgress = document.getElementById("ocr-progress");

    let videoStream = null;

    const orderMileage = document.getElementById("order-mileage");
    const orderFuel = document.getElementById("order-fuel");
    const orderComplaint = document.getElementById("order-complaint");
    const orderPhotoUrl = document.getElementById("order-photo-url");
    const btnSubmit = document.getElementById("btn-submit-order");
    const btnLogout = document.getElementById("btn-logout");

    // --- DIJAGRAM OŠTEĆENJA ---
    const carDiagramContainer = document.getElementById("car-diagram-container");
    const carSvg = document.getElementById("car-svg");
    const damageTypeSelect = document.getElementById("damage-type-select");
    const damageDescInput = document.getElementById("damage-desc-input");
    const damageList = document.getElementById("damage-list");

    let recordedDamages = [];

    carSvg.addEventListener("click", (e) => {
        const rect = carSvg.getBoundingClientRect();
        const xPercent = Math.round(((e.clientX - rect.left) / rect.width) * 100);
        const yPercent = Math.round(((e.clientY - rect.top) / rect.height) * 100);

        const type = damageTypeSelect.value;
        const note = damageDescInput.value.trim();
        const damageIndex = recordedDamages.length + 1;

        recordedDamages.push({
            id: damageIndex, x: xPercent, y: yPercent, type: type,
            description: note ? `${type} (${note})` : type
        });
        damageDescInput.value = "";
        renderDamageMarkers();
    });

    function renderDamageMarkers() {
        carDiagramContainer.querySelectorAll(".damage-pin").forEach((p) => p.remove());
        damageList.innerHTML = "";

        recordedDamages.forEach((d, idx) => {
            const pin = document.createElement("div");
            pin.className = "damage-pin";
            pin.style.left = `${d.x}%`;
            pin.style.top = `${d.y}%`;
            pin.textContent = idx + 1;
            pin.title = d.description;
            carDiagramContainer.appendChild(pin);

            const item = document.createElement("div");
            item.className = "damage-item";
            item.innerHTML = `
                <div>
                    <span class="damage-item-badge">${idx + 1}</span>
                    <strong>${escapeHtml(d.type)}</strong>
                    <span style="color: var(--text-muted); font-size: 0.8rem;">${d.description !== d.type ? "— " + escapeHtml(d.description) : ""} (X:${d.x}%, Y:${d.y}%)</span>
                </div>
                <button type="button" class="btn-remove-damage" data-index="${idx}">&times;</button>
            `;
            damageList.appendChild(item);
        });

        damageList.querySelectorAll(".btn-remove-damage").forEach((btn) => {
            btn.onclick = () => {
                const i = parseInt(btn.getAttribute("data-index"), 10);
                recordedDamages.splice(i, 1);
                renderDamageMarkers();
            };
        });
    }

    function escapeHtml(text) {
        const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
        return String(text).replace(/[&<>"']/g, (m) => map[m]);
    }

    // --- OCR ---
    async function processOcrBlob(blob) {
        ocrProgress.style.display = "block";
        ocrProgress.textContent = "⏳ Optičko čitanje...";

        try {
            const result = await Tesseract.recognize(blob, "srp+eng", {
                logger: (m) => {
                    if (m.status === "recognizing text") {
                        ocrProgress.textContent = `⏳ Očitavam (${Math.round(m.progress * 100)}%)...`;
                    }
                }
            });

            const extractedText = result.data.text;
            const formData = new FormData();
            formData.append("raw_text", extractedText);

            const res = await fetch("/api/v1/ocr/scan-license", { method: "POST", body: formData });
            ocrProgress.style.display = "none";

            if (!res.ok) throw new Error("Neuspešno parsiranje.");
            const data = await res.json();

            let popunjeno = [];
            if (data.license_plate && data.license_plate.trim()) {
                vehiclePlate.value = data.license_plate.trim();
                popunjeno.push(`Tablica: ${vehiclePlate.value}`);
            }
            if (data.owner_name && data.owner_name.trim()) {
                if (newCustomerName) newCustomerName.value = data.owner_name.trim();
                if (customerSearch) customerSearch.value = data.owner_name.trim();
                popunjeno.push(`Vlasnik: ${data.owner_name.trim()}`);
            }
            if (data.make && data.make.trim()) {
                vehicleMake.value = data.make.trim();
                popunjeno.push(`Marka: ${vehicleMake.value}`);
            }
            if (data.model && data.model.trim()) {
                vehicleModel.value = data.model.trim();
                popunjeno.push(`Model: ${vehicleModel.value}`);
            }
            if (data.vin && data.vin.trim()) {
                vehicleVin.value = data.vin.trim();
                popunjeno.push(`VIN: ${vehicleVin.value}`);
            }

            if (popunjeno.length > 0) {
                showAlert(`Dopunjeno: ${popunjeno.join(" | ")}`, "success");
            } else {
                showAlert("Nisu pronađeni podaci. Unesite ručno.", "error");
            }
        } catch (err) {
            ocrProgress.style.display = "none";
            showAlert("Greška: " + err.message, "error");
        }
    }

    // Kamera uživo sa crop-om
    async function startCamera() {
        try {
            const constraints = {
                video: { facingMode: { ideal: "environment" }, width: { ideal: 1920 }, height: { ideal: 1080 } },
                audio: false,
            };
            videoStream = await navigator.mediaDevices.getUserMedia(constraints);
            cameraVideo.srcObject = videoStream;
            cameraModal.classList.add("active");
        } catch (err) {
            console.error("Greška pri pristupu kameri:", err);
            showAlert("Kamera nije dostupna.", "error");
        }
    }

    function stopCamera() {
        if (videoStream) {
            videoStream.getTracks().forEach((track) => track.stop());
            videoStream = null;
        }
        cameraModal.classList.remove("active");
    }

    btnOpenLiveCam.addEventListener("click", () => {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            startCamera();
        } else {
            showAlert("Pretraživač ne podržava kameru.", "error");
        }
    });

    btnCloseCam.addEventListener("click", stopCamera);

    btnTakeSnapshot.addEventListener("click", () => {
        if (!videoStream) return;

        const vWidth = cameraVideo.videoWidth || 1280;
        const vHeight = cameraVideo.videoHeight || 720;
        const cropWidth = Math.round(vWidth * 0.85);
        const cropHeight = Math.round(vHeight * 0.55);
        const startX = Math.round((vWidth - cropWidth) / 2);
        const startY = Math.round((vHeight - cropHeight) / 2);

        cameraCanvas.width = cropWidth;
        cameraCanvas.height = cropHeight;
        const ctx = cameraCanvas.getContext("2d");
        ctx.drawImage(cameraVideo, startX, startY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);

        stopCamera();
        cameraCanvas.toBlob((blob) => { if (blob) processOcrBlob(blob); }, "image/jpeg", 0.95);
    });

    btnTriggerFileUpload.addEventListener("click", () => ocrFileInput.click());

    ocrFileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) processOcrBlob(file);
        ocrFileInput.value = "";
    });

    // Ručni unos (sakrij OCR)
    const btnSkipOcr = document.getElementById("btn-skip-ocr");
    if (btnSkipOcr) {
        btnSkipOcr.addEventListener("click", () => {
            document.querySelector(".ocr-box").style.display = "none";
            vehiclePlate.focus();
            showAlert("Popunite podatke ručno.", "success");
        });
    }

    // Pretraga klijenta
    customerSearch.addEventListener("input", async (e) => {
        const val = e.target.value.trim();
        if (val.length < 2) {
            customerResults.style.display = "none";
            return;
        }

        try {
            const customers = await ApiService.searchCustomers(val);
            customerResults.innerHTML = "";
            if (customers.length === 0) {
                customerResults.innerHTML = `<div class="search-item">+ Novi klijent "${escapeHtml(val)}"</div>`;
                customerResults.style.display = "block";
                customerResults.querySelector(".search-item").onclick = () => {
                    selectedCustomerId.value = "";
                    newCustomerFields.style.display = "block";
                    newCustomerName.value = val;
                    customerResults.style.display = "none";
                };
            } else {
                customers.forEach((c) => {
                    const item = document.createElement("div");
                    item.className = "search-item";
                    item.textContent = `${c.name || c.full_name} (${c.phone})`;
                    item.onclick = () => {
                        selectedCustomerId.value = c.id;
                        customerSearch.value = `${c.name || c.full_name} (${c.phone})`;
                        customerResults.style.display = "none";
                        newCustomerFields.style.display = "none";
                        loadCustomerVehicles(c.id);
                    };
                    customerResults.appendChild(item);
                });
                customerResults.style.display = "block";
            }
        } catch (err) { console.error(err); }
    });

    // Auto-popunjavanje vozila
    async function loadCustomerVehicles(customerId) {
        try {
            const res = await fetch(`/api/v1/vehicles/?customer_id=${customerId}`, {
                headers: ApiService.getHeaders(),
            });
            if (!res.ok) return;

            const vehicles = await res.json();
            if (!vehicles || vehicles.length === 0) {
                selectedVehicleId.value = "";
                vehiclePlate.value = "";
                vehicleMake.value = "";
                vehicleModel.value = "";
                vehicleVin.value = "";
                historyContainer.style.display = "none";
                vehiclePlate.focus();
                showAlert("Klijent nema vozila u sistemu.", "success");
                return;
            }

            if (vehicles.length === 1) {
                fillVehicleData(vehicles[0]);
                showAlert(`Vozilo popunjeno: ${vehicles[0].make} ${vehicles[0].model}`, "success");
            } else {
                showVehicleSelection(vehicles);
            }
        } catch (err) { console.error("Greška:", err); }
    }

    function fillVehicleData(v) {
        selectedVehicleId.value = v.id;
        vehiclePlate.value = v.license_plate || "";
        vehicleMake.value = v.make || "";
        vehicleModel.value = v.model || "";
        vehicleVin.value = v.vin || "";
        if (v.current_mileage) orderMileage.value = v.current_mileage;
        loadVehicleHistory(v.id);
    }

    function showVehicleSelection(vehicles) {
        vehicleResults.innerHTML = "";
        vehicles.forEach((v) => {
            const item = document.createElement("div");
            item.className = "search-item";
            item.textContent = `${v.license_plate} — ${v.make} ${v.model}`;
            item.onclick = () => {
                fillVehicleData(v);
                vehicleResults.style.display = "none";
            };
            vehicleResults.appendChild(item);
        });
        vehicleResults.style.display = "block";
        vehiclePlate.scrollIntoView({ behavior: "smooth", block: "center" });
        vehiclePlate.focus();
        showAlert(`Klijent ima ${vehicles.length} vozila. Izaberite vozilo.`, "success");
    }

    // Servisna knjižica
    async function loadVehicleHistory(vehicleId) {
        if (!vehicleId) {
            historyContainer.style.display = "none";
            return;
        }
        try {
            const res = await fetch(`/api/v1/vehicles/${vehicleId}/history`, {
                headers: ApiService.getHeaders(),
            });
            if (!res.ok) return;

            const history = await res.json();
            if (history.length === 0) {
                historyList.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted);">Novo vozilo — nema prethodnih servisa.</div>`;
                historyVisitsCount.textContent = "Novo vozilo";
            } else {
                historyVisitsCount.textContent = `${history.length} prethodnih servisa`;
                historyList.innerHTML = "";

                history.forEach((h) => {
                    const partsList = h.parts.map((p) =>
                        `<span class="history-part-pill">${p.is_part ? "⚙️" : "🔧"} ${p.title} (${p.quantity} kom)</span>`
                    ).join("");

                    const itemDiv = document.createElement("div");
                    itemDiv.className = "history-item";
                    itemDiv.innerHTML = `
                        <div class="history-item-top">
                            <span>${h.date} — #${h.order_number}</span>
                            <span class="history-item-mileage">${h.mileage.toLocaleString()} km</span>
                        </div>
                        <div class="history-item-complaint">${h.complaint || "Redovan servis"}</div>
                        <div>${partsList}</div>
                    `;
                    historyList.appendChild(itemDiv);
                });
            }
            historyContainer.style.display = "block";
        } catch (e) { console.error("Greška:", e); }
    }

    // Pretraga vozila po tablici
    vehiclePlate.addEventListener("input", async (e) => {
        const val = e.target.value.trim().toUpperCase();
        if (val.length < 2) {
            vehicleResults.style.display = "none";
            historyContainer.style.display = "none";
            return;
        }
        try {
            const vehicles = await ApiService.searchVehicles(val);
            vehicleResults.innerHTML = "";
            if (vehicles.length > 0) {
                vehicles.forEach((v) => {
                    const item = document.createElement("div");
                    item.className = "search-item";
                    item.textContent = `${v.license_plate} — ${v.make} ${v.model}`;
                    item.onclick = () => {
                        selectedVehicleId.value = v.id;
                        vehiclePlate.value = v.license_plate;
                        vehicleMake.value = v.make;
                        vehicleModel.value = v.model;
                        if (v.vin) vehicleVin.value = v.vin;
                        if (v.current_mileage) orderMileage.value = v.current_mileage;
                        vehicleResults.style.display = "none";
                        loadVehicleHistory(v.id);
                    };
                    vehicleResults.appendChild(item);
                });
                vehicleResults.style.display = "block";
            } else {
                selectedVehicleId.value = "";
                vehicleResults.style.display = "none";
                historyContainer.style.display = "none";
            }
        } catch (err) { console.error(err); }
    });

    // VIN dekoder
    vehicleVin.addEventListener("blur", async () => {
        const vin = vehicleVin.value.trim().toUpperCase();
        let indicator = document.getElementById("vin-indicator");

        if (!vin) {
            if (indicator) indicator.textContent = "";
            return;
        }

        if (vin.length !== 17) {
            if (indicator) {
                indicator.textContent = `⚠️ VIN mora imati 17 znakova (trenutno: ${vin.length}).`;
                indicator.style.color = "var(--warning)";
            }
            return;
        }

        if (indicator) {
            indicator.textContent = "🔍 Dekodiram VIN...";
            indicator.style.color = "var(--accent)";
        }

        try {
            const res = await fetch("/api/v1/vin/decode", {
                method: "POST",
                headers: ApiService.getHeaders(),
                body: JSON.stringify({ vin: vin }),
            });

            if (!res.ok) throw new Error("Greška.");
            const data = await res.json();

            if (!data.valid) {
                if (indicator) {
                    indicator.textContent = `❌ ${data.error || "Nevažeći VIN."}`;
                    indicator.style.color = "var(--danger)";
                }
                return;
            }

            let filled = [];
            if (data.make && !vehicleMake.value) {
                vehicleMake.value = data.make;
                filled.push(`Marka: ${data.make}`);
            }
            if (data.model && !vehicleModel.value) {
                vehicleModel.value = data.model;
                filled.push(`Model: ${data.model}`);
            }
            if (data.year) filled.push(`Godina: ${data.year}`);

            if (filled.length > 0 && indicator) {
                indicator.textContent = `✅ ${filled.join(" | ")} (${data.source})`;
                indicator.style.color = "var(--success)";
            } else if (indicator) {
                indicator.textContent = `ℹ️ ${data.message || "VIN prepoznat."}`;
                indicator.style.color = "var(--text-muted)";
            }
        } catch (err) {
            if (indicator) {
                indicator.textContent = `⚠️ Greška: ${err.message}`;
                indicator.style.color = "var(--warning)";
            }
        }
    });

    vehicleVin.addEventListener("input", () => {
        const indicator = document.getElementById("vin-indicator");
        if (indicator) indicator.textContent = "";
    });

    // Slanje naloga
    btnSubmit.addEventListener("click", async () => {
        try {
            let customerId = selectedCustomerId.value;

            if (!customerId) {
                const name = newCustomerName.value.trim();
                const phone = newCustomerPhone.value.trim();
                if (!name || !phone) {
                    showAlert("Unesite ime i telefon za novog klijenta.", "error");
                    return;
                }
                const newCust = await ApiService.createCustomer({ full_name: name, phone: phone });
                customerId = newCust.id;
            }

            let vehicleId = selectedVehicleId.value;

            if (!vehicleId) {
                const plate = vehiclePlate.value.trim().toUpperCase();
                const make = vehicleMake.value.trim();
                const model = vehicleModel.value.trim();
                const vin = vehicleVin.value.trim().toUpperCase();
                if (!plate || !make || !model) {
                    showAlert("Popunite registraciju, marku i model vozila.", "error");
                    return;
                }
                const newVeh = await ApiService.createVehicle({
                    customer_id: customerId,
                    license_plate: plate, make: make, model: model,
                    vin: vin || null,
                    current_mileage: parseInt(orderMileage.value, 10) || 0,
                });
                vehicleId = newVeh.id;
            }

            const mileage = parseInt(orderMileage.value, 10);
            const complaint = orderComplaint.value.trim();

            if (!mileage || !complaint) {
                showAlert("Unesite kilometražu i opis kvara.", "error");
                return;
            }

            const orderPayload = {
                vehicle_id: vehicleId,
                mileage_at_reception: mileage,
                fuel_level: orderFuel.value,
                complaint_description: complaint,
            };

            const createdOrder = await ApiService.createWorkOrder(orderPayload);

            if (recordedDamages.length > 0) {
                const summaryDamages = recordedDamages
                    .map((d, i) => `${i + 1}. ${d.description} na [X:${d.x}%, Y:${d.y}%]`)
                    .join(" | ");
                await ApiService.addWorkOrderPhoto(createdOrder.id, {
                    category: "INITIAL_DAMAGE",
                    photo_url: "https://images.unsplash.com/photo-1590362891991-f776e747a588?auto=format&fit=crop&w=600&q=80",
                    description: `Dijagram oštećenja: ${summaryDamages}`
                });
            }

            const photoUrl = orderPhotoUrl.value.trim();
            if (photoUrl) {
                await ApiService.addWorkOrderPhoto(createdOrder.id, {
                    category: "INITIAL_DAMAGE",
                    photo_url: photoUrl,
                    description: "Zatečeno stanje pri prijemu",
                });
            }

            showAlert(`Radni nalog #${createdOrder.order_number} je uspešno otvoren!\nToken: ${createdOrder.tracking_token}`, "success");

            orderComplaint.value = "";
            orderPhotoUrl.value = "";
            recordedDamages = [];
            renderDamageMarkers();

            setTimeout(() => { window.location.href = "/orders"; }, 1500);
        } catch (err) {
            showAlert(err.message, "error");
        }
    });

    // ODJAVA — koristi ApiService.logout()
    btnLogout.addEventListener("click", () => {
        ApiService.logout();
    });

    function showAlert(msg, type) {
        const alertBox = document.getElementById("alert-box");
        alertBox.textContent = msg;
        alertBox.className = `status-alert ${type}`;
        setTimeout(() => { alertBox.className = "status-alert"; }, 6000);
    }
});