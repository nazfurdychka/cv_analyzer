from openai_integration import open_ai_integration as aiing, openai_utils as ju
import model_script as md
import file_utils as flu

color_dict = {
    "GREEN_RGB": (0.078, 0.902, 0.710),
    "BLUE_RGB": (0.039, 0.765, 0.988),
    "PURPLE_RGB": (0.816, 0.443, 0.816),
    "YELLOW_COLOR_RGB": (1, 1, 0),
    "ORANGE_COLOR_RGB": (1, 0.7, 0.1)
}

RED_COLOR_RGB = (1, 0, 0)

color_to_index_dict = {index: color for index, color in enumerate(color_dict)}


def get_color_for_probability(probability, ranges):
    for color_name, (lower_bound, upper_bound) in ranges:
        if lower_bound < probability <= upper_bound:
            return color_name


def process_work_experience(response, file, ranges):
    prob_numerator = 0
    prob_denominator = 0
    text_by_color = {color: [] for color, _ in ranges}
    for experience in response.work_experience:
        for entry in experience.job_summary:
            probability = md.predict(entry)
            probability_scaled = probability * 100
            color = get_color_for_probability(probability_scaled, ranges)
            text_by_color[color].append(entry)
            prob_numerator += len(entry) * probability_scaled
            prob_denominator += len(entry)

    for color, entries in text_by_color.items():
        file = flu.highlight_processing(file, entries, color_dict[color])

    if prob_denominator == 0:
        general_probability = 0
    else:
        general_probability = prob_numerator / prob_denominator
    return file, general_probability


def process_companies(response, file):
    companies_list = []
    for experience in response.work_experience:
        companies_list.append(experience.company)
    check_companies_by_open_ai = aiing.check_companies(companies_list)
    check_companies_response = ju.parse_open_ai_check_response(check_companies_by_open_ai)
    fake_companies_list = []
    for check_result in check_companies_response.check_results:
        if check_result.doesExist is False:
            fake_companies_list.append(check_result.entity)
    return flu.highlight_processing(file, fake_companies_list, RED_COLOR_RGB)


def process_education(response, file):
    check_educ_by_open_ai = aiing.check_education(response.educ_info)
    check_educ_response = ju.parse_open_ai_check_response(check_educ_by_open_ai)
    fake_educ = []
    for check_result in check_educ_response.check_results:
        if check_result.doesExist is False:
            fake_educ.append(check_result.entity)
    return flu.highlight_processing(file, fake_educ, RED_COLOR_RGB)


def process_colours_for_ranges(ranges):
    color_ranges = []
    for index, num_range in ranges:
        color_name = color_to_index_dict.get(index)
        color_ranges.append((color_name, num_range))
    return color_ranges


def generate_ranges_with_colours(n):
    full_value = 100
    range_size = full_value / n
    start = 0
    ranges = []
    for i in range(n):
        end = start + range_size
        ranges.append((i, (start, end)))
        start = end
    return process_colours_for_ranges(ranges)


def process_cv(file, num_of_ranges):
    ranges = generate_ranges_with_colours(num_of_ranges)
    converted_text = flu.convert_to_text(file)
    parse_by_open_ai = aiing.parse_resume(converted_text)
    response = ju.parse_open_ai_response(parse_by_open_ai)
    processed_companies_file = process_companies(response, file)
    processed_education_file = process_education(response, processed_companies_file)
    return process_work_experience(response, processed_education_file, ranges)
