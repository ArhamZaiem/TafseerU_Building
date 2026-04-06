def build_prompt(surah, ayah):
    return f"""

Task: Summarize this into English 

Structure:

Main Themes of the Ayah:
1. ...
2. ...
3. ...
4. ...

Summary:
...


Rules:
- Analyze the attached JSON file completely
- After analysing the json, identify the main themes of the aayah
- Return no more than 4 major themes, each in one word
- if the aayah naturally contains only 1, 2 or 3 themes then return only those themes, do not force it to be 4 themes
- Do not create themes that are not present in the aayah, be faithful to the original meaning and content of the aayah
- Do not create artificial themes just to reach 4
- Summarize the aayah from the JSON in complete sentences, do not use incomplete sentences or sentence fragments
- if there is a spritual element in it or anything related to practical affairs or action related affairs do not forget to include it, if there is only then.
- Do not force the inclusion of spirituality or action related themes if they are not present in the aayah, be faithful to the original content and meaning of the aayah
- do not leave out anything importing which should be covered it in, with regards to the sprituality, diferrence of opinions, the action related part, present them in a summarised form though, following the command given just above this 
- do not divert from the original meaning
- do not miss out on the important points given the context of the readers
- be faithful in the translation and do not hallucinate
- do not break sentences or use incomplete sentences
- statements should be easily understandable as given the context of the audience
- this will be read by locals and laymen so do not use complex language
- also maintain the scholarly tone but as i said make it more reader's focused language 
- if there's a need for bullet points for making the understanding easy use that, *do not go overboard with bullet points*
- i want the usage of pragraph style too, but I want bullet points too for better readability and understanding, so I am leaving it onto you, but do not go overboard with either of the too
- give the output directly, without stating anything else
- use only the attached JSON file as your source

The attached file corresponds to:
- Surah: {surah}
- Ayah: {ayah}

Output:
A clear, structured English summary.
"""
