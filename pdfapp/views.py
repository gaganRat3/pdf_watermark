from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import PDFUploadForm, WatermarkForm, MergePDFForm, CustomFileNameForm
import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

def home(request):
	if request.method == 'POST':
		pdf_form = PDFUploadForm(request.POST, request.FILES)
		watermark_form = WatermarkForm(request.POST)
		merge_form = MergePDFForm(request.POST, request.FILES)
		custom_name_form = CustomFileNameForm(request.POST)
		if pdf_form.is_valid() and watermark_form.is_valid() and merge_form.is_valid() and custom_name_form.is_valid():
			pdf_file = pdf_form.cleaned_data['pdf_file']
			watermark_text = watermark_form.cleaned_data['watermark']
			# Keep the original selection for color mapping (before possible suffix append)
			selected_choice = watermark_form.cleaned_data['watermark']

			# normalize choice to a simple key (lowercase, alphanumeric)
			def _normalize_choice(s):
				import re
				if not s:
					return ''
				return re.sub(r'[^0-9a-z]', '', s.lower())

			# map normalized keys to RGB colors
			_color_map = {
				# red
				'bhudevnetworkvivahcom': (0.78, 0.08, 0.08),
				'bhudevnetworkvivah': (0.78, 0.08, 0.08),
				'divorce': (0.78, 0.08, 0.08),
				'masters': (0.78, 0.08, 0.08),
				'master': (0.78, 0.08, 0.08),
				'maharashtra': (0.78, 0.08, 0.08),

# purple
'nri': (0.45, 0.12, 0.65),
'saurashtra': (0.45, 0.12, 0.65),
'govjob': (0.45, 0.12, 0.65),
'sg': (0.45, 0.12, 0.65),
'ng': (0.45, 0.12, 0.65),
'1012': (0.45, 0.12, 0.65),
'canada': (0.45, 0.12, 0.65),
'usa': (0.45, 0.12, 0.65),
'ausnz': (0.45, 0.12, 0.65),
'europe': (0.45, 0.12, 0.65),
'mumbai': (0.45, 0.12, 0.65),
'amdavad': (0.45, 0.12, 0.65),
'vadodara': (0.45, 0.12, 0.65),
'jamnagar': (0.45, 0.12, 0.65),
'bhavnagar': (0.45, 0.12, 0.65),


				# sky blue
				'doctor': (0.20, 0.65, 0.90),

				# yellow
				'cacs': (0.95, 0.76, 0.07),
				'40plus': (0.95, 0.76, 0.07),
			}

			_choice_key = _normalize_choice(selected_choice)
			color_rgb = _color_map.get(_choice_key, (0.78, 0.08, 0.08))

			# create a lighter version of the color for the centered watermark
			# mix factor: 0.0 = original color, 1.0 = white
			# lowered mixing and increased alpha to make the center watermark a bit darker
			_mix_to_white = 0.40
			lighter_rgb = tuple(color_rgb[i] * (1 - _mix_to_white) + _mix_to_white * 1.0 for i in range(3))
			# centered watermark alpha (increase to make it more visible)
			_center_alpha = 0.32

			# If the selected watermark already contains a dot (a domain), don't append suffix.
			# Otherwise append the standard suffix to form 'NAME.bhudevnetworkvivah.com'
			suffix = '.bhudevnetworkvivah.com'
			if '.' in watermark_text:
				final_watermark = watermark_text
			else:
				if watermark_text.endswith(suffix):
					final_watermark = watermark_text
				else:
					final_watermark = f"{watermark_text}{suffix}"
			watermark_text = final_watermark
			pdf_file_2 = merge_form.cleaned_data.get('pdf_file_2')
			city = custom_name_form.cleaned_data.get('city', '')
			name = custom_name_form.cleaned_data.get('name', '')
			date = custom_name_form.cleaned_data.get('date', '')
			education = custom_name_form.cleaned_data.get('education', '')

			# Save uploaded PDF temporarily
			pdf_path = f'temp_{pdf_file.name}'
			with open(pdf_path, 'wb+') as destination:
				for chunk in pdf_file.chunks():
					destination.write(chunk)

			# Apply watermark per page (2 watermarks: top-right + centered tilted)
			pdf_reader = PdfReader(pdf_path)
			pdf_writer = PdfWriter()
			for page in pdf_reader.pages:
				# determine page size
				try:
					page_width = float(page.mediabox.width)
					page_height = float(page.mediabox.height)
				except Exception:
					# fallback to letter
					page_width, page_height = letter

				# create watermark for this page size
				wm_io = BytesIO()
				c = canvas.Canvas(wm_io, pagesize=(page_width, page_height))

				# top-right watermark size (change multiplier to tune size)
				# e.g. 0.03 = larger, 0.025 = medium, 0.02 = smaller
				small_font = max(14, int(page_width * 0.03))
				margin = 20
				tx = page_width - margin
				ty = page_height - margin - small_font
				# no glow: draw the main dark watermark text

				# create a subtle shiny top-right red watermark
				text_width_small = c.stringWidth(watermark_text, "Helvetica-Bold", small_font)
				left = tx - text_width_small
				# draw a thin white shine bar above the text
				try:
					shine_w = max(text_width_small * 0.6, small_font * 1.8)
					shine_h = max(small_font * 0.22, 3)
					shine_x = left + (text_width_small - shine_w) / 2.0
					shine_y = ty + small_font * 0.35
					c.setFillColorRGB(1, 1, 1, alpha=0.22)
					c.roundRect(shine_x, shine_y, shine_w, shine_h, radius=shine_h / 2.0, fill=1, stroke=0)
				except Exception:
					pass
				# draw watermark text on top (bold and larger) using chosen color
				c.setFont("Helvetica-Bold", small_font)
				c.setFillColorRGB(color_rgb[0], color_rgb[1], color_rgb[2], alpha=0.98)
				c.drawRightString(tx, ty, watermark_text)

				# centered large tilted watermark - make noticeably smaller and fit the page
				import math
				# start with a font based on the shorter page dimension (adjustable)
				# If you want the center watermark bigger/smaller, change the multiplier below (0.07 -> bigger, 0.05 -> smaller)
				large_font = max(20, int(min(page_width, page_height) * 0.07))
				# compute text width at initial size
				text_width = c.stringWidth(watermark_text, "Helvetica", large_font)
				# diagonal length for the page and allow smaller coverage
				diagonal = math.hypot(page_width, page_height)
				# limit rotated watermark width to a fraction of diagonal
				# Increase this fraction to let the watermark cover more space (e.g., 0.55) or reduce to shrink it
				max_width = diagonal * 0.48
				if text_width > 0 and text_width > max_width:
					scale = max_width / text_width
					large_font = max(12, int(large_font * scale))
				# use chosen color and increased opacity for the centered watermark
				c.setFont("Helvetica-Bold", large_font)
				# center watermark color (lighter variant, much lower opacity)
				c.setFillColorRGB(lighter_rgb[0], lighter_rgb[1], lighter_rgb[2], alpha=_center_alpha)
				c.saveState()
				# center and rotate slightly less to reduce effective span
				c.translate(page_width / 2.0, page_height / 2.0)
				c.rotate(25)
				# compute text width for center shine overlay
				tw = c.stringWidth(watermark_text, "Helvetica-Bold", large_font)
				# removed center white shine overlay to avoid a visible white line across the centered watermark
				c.setFillColorRGB(lighter_rgb[0], lighter_rgb[1], lighter_rgb[2], alpha=_center_alpha)
				c.drawCentredString(0, 0, watermark_text)
				c.restoreState()

				c.save()
				wm_io.seek(0)

				watermark_reader = PdfReader(wm_io)
				watermark_page = watermark_reader.pages[0]
				page.merge_page(watermark_page)
				pdf_writer.add_page(page)

			# If second PDF is uploaded, merge it
			if pdf_file_2:
				pdf_path_2 = f'temp_{pdf_file_2.name}'
				with open(pdf_path_2, 'wb+') as destination:
					for chunk in pdf_file_2.chunks():
						destination.write(chunk)
				pdf_reader_2 = PdfReader(pdf_path_2)
				for page in pdf_reader_2.pages:
					pdf_writer.add_page(page)
				os.remove(pdf_path_2)

			# Build custom filename
			custom_filename = f"{city}_{name}_{date}_{education}.pdf".replace(' ', '_')
			download_name = custom_filename if custom_filename != "____.pdf" else "output.pdf"

			# Write final PDF to memory to avoid creating another temp file
			output_io = BytesIO()
			pdf_writer.write(output_io)
			output_io.seek(0)

			# Clean up temporary input files if they exist (defensive)
			try:
				if os.path.exists(pdf_path):
					os.remove(pdf_path)
			except Exception:
				pass
			# pdf_path_2 may or may not exist depending on whether a second file was uploaded
			try:
				if 'pdf_path_2' in locals() and os.path.exists(pdf_path_2):
					os.remove(pdf_path_2)
			except Exception:
				pass

			response = HttpResponse(output_io.read(), content_type='application/pdf')
			response['Content-Disposition'] = f'attachment; filename="{download_name}"'
			return response
	else:
		pdf_form = PDFUploadForm()
		watermark_form = WatermarkForm(initial={'watermark': 'bhudevnetworkvivah.com'})
		merge_form = MergePDFForm()
		custom_name_form = CustomFileNameForm()
	return render(request, 'pdfapp/home.html', {
		'pdf_form': pdf_form,
		'watermark_form': watermark_form,
		'merge_form': merge_form,
		'custom_name_form': custom_name_form,
	})
