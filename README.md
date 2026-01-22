# LoRaWAN Security Analysis - Academic Project

This repository contains materials developed as part of a university academic project focused on the security analysis of LoRaWAN wireless networks.

The project combines passive monitoring of LoRaWAN communication using SDR techniques with controlled, timing-based interference experiments performed in a laboratory environment. The objective is to analyze protocol behavior, availability limitations, and security properties of LoRaWAN under realistic but controlled conditions.

## Repository Structure

The repository is organized into the following directories:

- GNU Radio/
  Contains GNU Radio flowgraphs and supporting files used for passive reception, synchronization, and processing of LoRa signals. The flowgraphs are used to receive LoRa frames via SDR hardware and forward demodulated data over UDP for further processing.
  
  Included files:
  - Recenter.grc - GNU Radio flowgraph for baseband signal centering
  - usrp_LoRa_decode_to_UDP.grc - Flowgraph for LoRa signal reception and forwarding to UDP
  - Recenter.pdf - Documentation of the recentering flowgraph
  - LoRa_receive_to_UDP_RTL_SDR.pdf - Flowgraph overview for RTL-SDR reception
  - decode.py - Python script for decoding LoRaWAN frames received via UDP

- LoStik-python/
  Contains Python scripts used for controlled, timing-based radio-frequency interference experiments using a LoStik USB LoRa device. The scripts interact with the device via a serial interface and are used to analyze the impact of interference on LoRaWAN communication.
  
  Included files:
  - confirmed_uplink_interference.py - Interference experiment targeting confirmed uplink communication
  - lorawan_join_interference.py - Interference experiment targeting the OTAA join procedure

- Modified LA66 fw/
  Contains a modified firmware image for the LA66 USB LoRaWAN adapter. The firmware is based on the official LA66 SDK and was adapted to support controlled experimental behavior in a laboratory environment.
  
  Included files:
  - DRAGINO-LRWAN-AT-custom-ysec.bin - Precompiled firmware image for the LA66 device

## External Resources and References

The development of this project was strongly based on existing open-source tools, documentation, and security analyses, including:

- gr-lora_sdr - GNU Radio blocks for LoRa signal demodulation and analysis  
  https://github.com/tapparelj/gr-lora_sdr

- LoRaCraft - GNU Radio-based LoRa physical layer implementation  
  https://github.com/PentHertz/LoRa_Craft

- Y-Security - Security of LoRaWAN  
  https://www.y-security.de/news-en/security-of-lorawan/

These resources were used as references and building blocks for understanding LoRa modulation, LoRaWAN protocol behavior, and known security limitations.

## Scope and Limitations

All experiments were conducted in a controlled laboratory environment using dedicated hardware. The repository is intended for educational and research purposes only and does not provide production-ready or offensive tooling.

## Disclaimer

This project was developed strictly for academic and educational purposes.
All experiments were performed in a controlled laboratory environment.
The author does not condone or encourage unauthorized interference with wireless communications.
